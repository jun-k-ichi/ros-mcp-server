import argparse
import io
import json
import os
import time
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from PIL import Image as PILImage

# Import tools
from tools.ros_actions import register_action_tools
from tools.ros_services import register_service_tools

# Import utils
from utils.config_utils import get_robot_specifications, parse_robot_config
from utils.network_utils import ping_ip_and_port
from utils.websocket_manager import WebSocketManager, parse_image, parse_json

# ROS bridge connection settings
ROSBRIDGE_IP = "127.0.0.1"  # Default is localhost. Replace with your local IPor set using the LLM.
ROSBRIDGE_PORT = (
    9090  # Rosbridge default is 9090. Replace with your rosbridge port or set using the LLM.
)

# MCP transport settings - will be set from command line arguments
MCP_TRANSPORT = "stdio"  # Default is stdio.

# MCP connection settings (streamable-http) - will be set from command line arguments
MCP_HOST = "127.0.0.1"  # Default is localhost. Replace with the address of your remote MCP server.

# MCP port settings (default=9000) - will be set from command line arguments
MCP_PORT = 9000  # Default is 9000. Replace with the port of your remote MCP server.

# Initialize MCP server and WebSocket manager
mcp = FastMCP("ros-mcp-server")
ws_manager = WebSocketManager(
    ROSBRIDGE_IP, ROSBRIDGE_PORT, default_timeout=5.0
)  # Increased default timeout for ROS operations


# Register all ROS tools
register_service_tools(mcp, ws_manager)
register_action_tools(mcp, ws_manager)


@mcp.tool(description=("Get robot configuration from YAML file."))
def get_robot_config(name: str) -> dict:
    """
    Get the robot configuration from the YAML file for connecting to the robot and knowing its capabilities.

    Returns:
        dict: The robot configuration.
    """
    robot_config = parse_robot_config(name)

    if len(robot_config) > 1:
        return {
            "error": f"Multiple configurations found for robot '{name}'. Please specify a more precise name."
        }
    elif not robot_config:
        return {
            "error": f"No configuration found for robot '{name}'. Please check the name and try again. Or you can set the IP/port manually using the 'connect_to_robot' tool."
        }
    return {"robot_config": robot_config}


@mcp.tool(
    description=("List all available robot specifications that can be used with get_robot_config.")
)
def list_verified_robot_specifications() -> dict:
    """
    Get a list of all available robot specification files.

    Returns:
        dict: List of available robot names that can be used with get_robot_config.
    """
    return get_robot_specifications()


@mcp.tool(
    description=(
        "After getting the robot config, connect to the robot by setting the IP/port and testing connectivity."
    )
)
def connect_to_robot(
    ip: str = ROSBRIDGE_IP,
    port: int = ROSBRIDGE_PORT,
    ping_timeout: float = 2.0,
    port_timeout: float = 2.0,
) -> dict:
    """
    Connect to a robot by setting the IP and port for the WebSocket connection, then testing connectivity.

    Args:
        ip (Optional[str]): The IP address of the rosbridge server. Defaults is localhost.
        port (Optional[int]): The port number of the rosbridge server. Defaults to 9090.
        ping_timeout (float): Timeout for ping in seconds. Default = 2.0.
        port_timeout (float): Timeout for port check in seconds. Default = 2.0.

    Returns:
        dict: Connection status with ping and port check results.
    """

    # Set default values if None
    actual_ip = str(ip).strip() if ip else "localhost"
    actual_port = int(port) if port else 9090

    # Fix truncated IP addresses (MCP sometimes truncates "127.0.0.1" to "127")
    if actual_ip == "127":
        actual_ip = "127.0.0.1"

    # Fix truncated IP addresses (MCP sometimes truncates "127.0.0.1" to "127")
    if actual_ip == "127":
        actual_ip = "127.0.0.1"

    # Set the IP and port
    ws_manager.set_ip(actual_ip, actual_port)

    # Test connectivity
    ping_result = ping_ip_and_port(actual_ip, actual_port, ping_timeout, port_timeout)

    # Combine the results
    return {
        "message": f"WebSocket IP set to {actual_ip}:{actual_port}",
        "connectivity_test": ping_result,
    }


@mcp.tool(description=("Fetch available topics from the ROS bridge.\nExample:\nget_topics()"))
def get_topics() -> dict:
    """
    Fetch available topics from the ROS bridge.

    Returns:
        dict: Contains two lists - 'topics' and 'types',
            or a message string if no topics are found.
    """
    # rosbridge service call to get topic list
    message = {
        "op": "call_service",
        "service": "/rosapi/topics",
        "type": "rosapi/Topics",
        "id": "get_topics_request_1",
    }

    # Request topic list from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return topic info if present
    if response and "values" in response:
        return response["values"]
    else:
        return {"warning": "No topics found"}


@mcp.tool(
    description=("Get the message type for a specific topic.\nExample:\nget_topic_type('/cmd_vel')")
)
def get_topic_type(topic: str) -> dict:
    """
    Get the message type for a specific topic.

    Args:
        topic (str): The topic name (e.g., '/cmd_vel')

    Returns:
        dict: Contains the 'type' field with the message type,
            or an error message if topic doesn't exist.
    """
    # Validate input
    if not topic or not topic.strip():
        return {"error": "Topic name cannot be empty"}

    # rosbridge service call to get topic type
    message = {
        "op": "call_service",
        "service": "/rosapi/topic_type",
        "type": "rosapi/TopicType",
        "args": {"topic": topic},
        "id": f"get_topic_type_request_{topic.replace('/', '_')}",
    }

    # Request topic type from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return topic type if present
    if response and "values" in response:
        topic_type = response["values"].get("type", "")
        if topic_type:
            return {"topic": topic, "type": topic_type}
        else:
            return {"error": f"Topic {topic} does not exist or has no type"}
    else:
        return {"error": f"Failed to get type for topic {topic}"}


@mcp.tool(
    description=(
        "Get the complete structure/definition of a message type.\n"
        "Example:\n"
        "get_message_details('geometry_msgs/Twist')"
    )
)
def get_message_details(message_type: str) -> dict:
    """
    Get the complete structure/definition of a message type.

    Args:
        message_type (str): The message type (e.g., 'geometry_msgs/Twist')

    Returns:
        dict: Contains the message structure with field names and types,
            or an error message if the message type doesn't exist.
    """
    # Validate input
    if not message_type or not message_type.strip():
        return {"error": "Message type cannot be empty"}

    # rosbridge service call to get message details
    message = {
        "op": "call_service",
        "service": "/rosapi/message_details",
        "type": "rosapi/MessageDetails",
        "args": {"type": message_type},
        "id": f"get_message_details_request_{message_type.replace('/', '_')}",
    }

    # Request message details from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return message structure if present
    if response and "values" in response:
        typedefs = response["values"].get("typedefs", [])
        if typedefs:
            # Parse the structure into a more readable format
            structure = {}
            for typedef in typedefs:
                type_name = typedef.get("type", message_type)
                field_names = typedef.get("fieldnames", [])
                field_types = typedef.get("fieldtypes", [])

                fields = {}
                for name, ftype in zip(field_names, field_types):
                    fields[name] = ftype

                structure[type_name] = {"fields": fields, "field_count": len(fields)}

            return {"message_type": message_type, "structure": structure}
        else:
            return {"error": f"Message type {message_type} not found or has no definition"}
    else:
        return {"error": f"Failed to get details for message type {message_type}"}


@mcp.tool(
    description=(
        "Get list of nodes that are publishing to a specific topic.\n"
        "Example:\n"
        "get_publishers_for_topic('/cmd_vel')"
    )
)
def get_publishers_for_topic(topic: str) -> dict:
    """
    Get list of nodes that are publishing to a specific topic.

    Args:
        topic (str): The topic name (e.g., '/cmd_vel')

    Returns:
        dict: Contains list of publisher node names,
            or a message if no publishers found.
    """
    # Validate input
    if not topic or not topic.strip():
        return {"error": "Topic name cannot be empty"}

    # rosbridge service call to get publishers
    message = {
        "op": "call_service",
        "service": "/rosapi/publishers",
        "type": "rosapi/Publishers",
        "args": {"topic": topic},
        "id": f"get_publishers_for_topic_request_{topic.replace('/', '_')}",
    }

    # Request publishers from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return publishers if present
    if response and "values" in response:
        publishers = response["values"].get("publishers", [])
        return {"topic": topic, "publishers": publishers, "publisher_count": len(publishers)}
    else:
        return {"error": f"Failed to get publishers for topic {topic}"}


@mcp.tool(
    description=(
        "Get list of nodes that are subscribed to a specific topic.\n"
        "Example:\n"
        "get_subscribers_for_topic('/cmd_vel')"
    )
)
def get_subscribers_for_topic(topic: str) -> dict:
    """
    Get list of nodes that are subscribed to a specific topic.

    Args:
        topic (str): The topic name (e.g., '/cmd_vel')

    Returns:
        dict: Contains list of subscriber node names,
            or a message if no subscribers found.
    """
    # Validate input
    if not topic or not topic.strip():
        return {"error": "Topic name cannot be empty"}

    # rosbridge service call to get subscribers
    message = {
        "op": "call_service",
        "service": "/rosapi/subscribers",
        "type": "rosapi/Subscribers",
        "args": {"topic": topic},
        "id": f"get_subscribers_for_topic_request_{topic.replace('/', '_')}",
    }

    # Request subscribers from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return subscribers if present
    if response and "values" in response:
        subscribers = response["values"].get("subscribers", [])
        return {"topic": topic, "subscribers": subscribers, "subscriber_count": len(subscribers)}
    else:
        return {"error": f"Failed to get subscribers for topic {topic}"}


@mcp.tool(
    description=(
        "Get comprehensive information about all ROS topics including publishers, subscribers, and message types.\n"
        "Example:\n"
        "inspect_all_topics()"
    )
)
def inspect_all_topics() -> dict:
    """
    Get comprehensive information about all ROS topics including publishers, subscribers, and message types.

    Returns:
        dict: Contains detailed information about all topics including:
            - Topic names and message types
            - Publishers for each topic
            - Subscribers for each topic
            - Connection counts and statistics
    """
    # First get all topics
    topics_message = {
        "op": "call_service",
        "service": "/rosapi/topics",
        "type": "rosapi/Topics",
        "args": {},
        "id": "inspect_all_topics_request_1",
    }

    with ws_manager:
        topics_response = ws_manager.request(topics_message)

        if not topics_response or "values" not in topics_response:
            return {"error": "Failed to get topics list"}

        topics = topics_response["values"].get("topics", [])
        types = topics_response["values"].get("types", [])
        topic_details = {}

        # Get details for each topic
        topic_errors = []
        for i, topic in enumerate(topics):
            # Get topic type
            topic_type = types[i] if i < len(types) else "unknown"

            # Get publishers for this topic
            publishers_message = {
                "op": "call_service",
                "service": "/rosapi/publishers",
                "type": "rosapi/Publishers",
                "args": {"topic": topic},
                "id": f"get_publishers_{topic.replace('/', '_')}",
            }

            publishers_response = ws_manager.request(publishers_message)
            publishers = []
            if publishers_response and "values" in publishers_response:
                publishers = publishers_response["values"].get("publishers", [])
            elif publishers_response and "error" in publishers_response:
                topic_errors.append(f"Topic {topic} publishers: {publishers_response['error']}")

            # Get subscribers for this topic
            subscribers_message = {
                "op": "call_service",
                "service": "/rosapi/subscribers",
                "type": "rosapi/Subscribers",
                "args": {"topic": topic},
                "id": f"get_subscribers_{topic.replace('/', '_')}",
            }

            subscribers_response = ws_manager.request(subscribers_message)
            subscribers = []
            if subscribers_response and "values" in subscribers_response:
                subscribers = subscribers_response["values"].get("subscribers", [])
            elif subscribers_response and "error" in subscribers_response:
                topic_errors.append(f"Topic {topic} subscribers: {subscribers_response['error']}")

            topic_details[topic] = {
                "type": topic_type,
                "publishers": publishers,
                "subscribers": subscribers,
                "publisher_count": len(publishers),
                "subscriber_count": len(subscribers),
            }

        return {
            "total_topics": len(topics),
            "topics": topic_details,
            "topic_errors": topic_errors,  # Include any errors encountered during inspection
        }


@mcp.tool(
    description=(
        "Subscribe to a ROS topic and return the first message received.\n"
        "Example:\n"
        "subscribe_once(topic='/cmd_vel', msg_type='geometry_msgs/msg/TwistStamped')\n"
        "subscribe_once(topic='/slow_topic', msg_type='my_package/SlowMsg', timeout=None)  # Specify timeout only if topic publishes infrequently\n"
        "subscribe_once(topic='/high_rate_topic', msg_type='sensor_msgs/Image', timeout=None, queue_length=5, throttle_rate_ms=100)  # Control message buffering and rate"
    )
)
def subscribe_once(
    topic: str = "",
    msg_type: str = "",
    timeout: Optional[float] = None,
    queue_length: Optional[int] = None,
    throttle_rate_ms: Optional[int] = None,
) -> dict:
    """
    Subscribe to a given ROS topic via rosbridge and return the first message received.

    Args:
        topic (str): The ROS topic name (e.g., "/cmd_vel", "/joint_states").
        msg_type (str): The ROS message type (e.g., "geometry_msgs/Twist").
        timeout (Optional[float]): Timeout in seconds. If None, uses the default timeout.
        queue_length (Optional[int]): How many messages to buffer before dropping old ones. Must be ≥ 1.
        throttle_rate_ms (Optional[int]): Minimum interval between messages in milliseconds. Must be ≥ 0.

    Returns:
        dict:
            - {"msg": <parsed ROS message>} if successful
            - {"error": "<error message>"} if subscription or timeout fails
    """
    # Validate critical args before attempting subscription
    if not topic or not msg_type:
        return {"error": "Missing required arguments: topic and msg_type must be provided."}

    # Validate optional parameters
    if queue_length is not None and (not isinstance(queue_length, int) or queue_length < 1):
        return {"error": "queue_length must be an integer ≥ 1"}

    if throttle_rate_ms is not None and (
        not isinstance(throttle_rate_ms, int) or throttle_rate_ms < 0
    ):
        return {"error": "throttle_rate_ms must be an integer ≥ 0"}

    # Construct the rosbridge subscribe message
    subscribe_msg: dict = {
        "op": "subscribe",
        "topic": topic,
        "type": msg_type,
    }

    # Add optional parameters if provided
    if queue_length is not None:
        subscribe_msg["queue_length"] = queue_length

    if throttle_rate_ms is not None:
        subscribe_msg["throttle_rate"] = throttle_rate_ms

    # Subscribe and wait for the first message
    with ws_manager:
        # Send subscription request
        send_error = ws_manager.send(subscribe_msg)
        if send_error:
            return {"error": f"Failed to subscribe: {send_error}"}

        # Use default timeout if none specified
        actual_timeout = timeout if timeout is not None else ws_manager.default_timeout

        # Loop until we receive the first message or timeout
        end_time = time.time() + actual_timeout
        while time.time() < end_time:
            response = ws_manager.receive(timeout=0.5)  # non-blocking small timeout
            if response is None:
                continue  # idle timeout: no frame this tick

            if "Image" in msg_type:
                msg_data = parse_image(response)
            else:
                msg_data = parse_json(response)

            if not msg_data:
                continue  # non-JSON or empty

            # Check for status errors from rosbridge
            if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                return {"error": f"Rosbridge error: {msg_data.get('msg', 'Unknown error')}"}

            # Check for the first published message
            if msg_data.get("op") == "publish" and msg_data.get("topic") == topic:
                # Unsubscribe before returning the message
                unsubscribe_msg = {"op": "unsubscribe", "topic": topic}
                ws_manager.send(unsubscribe_msg)
                if "Image" in msg_type:
                    return {
                        "message": "Image received successfully and saved in the MCP server. Run the 'analyze_image' tool to analyze it"
                    }
                else:
                    return {"msg": msg_data.get("msg", {})}

        # Timeout - unsubscribe and return error
        unsubscribe_msg = {"op": "unsubscribe", "topic": topic}
        ws_manager.send(unsubscribe_msg)
        return {"error": "Timeout waiting for message from topic"}


@mcp.tool(
    description=(
        "Publish a single message to a ROS topic.\n"
        "Example:\n"
        "publish_once(topic='/cmd_vel', msg_type='geometry_msgs/msg/TwistStamped', msg={'linear': {'x': 1.0}})"
    )
)
def publish_once(topic: str = "", msg_type: str = "", msg: dict = {}) -> dict:
    """
    Publish a single message to a ROS topic via rosbridge.

    Args:
        topic (str): ROS topic name (e.g., "/cmd_vel")
        msg_type (str): ROS message type (e.g., "geometry_msgs/Twist")
        msg (dict): Message payload as a dictionary

    Returns:
        dict:
            - {"success": True} if sent without errors
            - {"error": "<error message>"} if connection/send failed
            - If rosbridge responds (usually it doesn’t for publish), parsed JSON or error info
    """
    # Validate critical args before attempting publish
    if not topic or not msg_type or msg == {}:
        return {
            "error": "Missing required arguments: topic, msg_type, and msg must all be provided."
        }

    # Use proper advertise → publish → unadvertise pattern
    with ws_manager:
        # 1. Advertise the topic
        advertise_msg = {"op": "advertise", "topic": topic, "type": msg_type}
        send_error = ws_manager.send(advertise_msg)
        if send_error:
            return {"error": f"Failed to advertise topic: {send_error}"}

        # Check for advertise response/errors
        response = ws_manager.receive(timeout=1.0)
        if response:
            try:
                msg_data = json.loads(response)
                if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                    return {"error": f"Advertise failed: {msg_data.get('msg', 'Unknown error')}"}
            except json.JSONDecodeError:
                pass  # Non-JSON response is usually fine for advertise

        # 2. Publish the message
        publish_msg = {"op": "publish", "topic": topic, "msg": msg}
        send_error = ws_manager.send(publish_msg)
        if send_error:
            # Try to unadvertise even if publish failed
            ws_manager.send({"op": "unadvertise", "topic": topic})
            return {"error": f"Failed to publish message: {send_error}"}

        # Check for publish response/errors
        response = ws_manager.receive(timeout=1.0)
        if response:
            try:
                msg_data = json.loads(response)
                if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                    # Unadvertise before returning error
                    ws_manager.send({"op": "unadvertise", "topic": topic})
                    return {"error": f"Publish failed: {msg_data.get('msg', 'Unknown error')}"}
            except json.JSONDecodeError:
                pass  # Non-JSON response is usually fine for publish

        # 3. Unadvertise the topic
        unadvertise_msg = {"op": "unadvertise", "topic": topic}
        ws_manager.send(unadvertise_msg)

    return {
        "success": True,
        "note": "Message published using advertise → publish → unadvertise pattern",
    }


@mcp.tool(
    description=(
        "Subscribe to a topic for a duration and collect messages.\n"
        "Example:\n"
        "subscribe_for_duration(topic='/cmd_vel', msg_type='geometry_msgs/msg/TwistStamped', duration=5, max_messages=10)\n"
        "subscribe_for_duration(topic='/high_rate_topic', msg_type='sensor_msgs/Image', duration=10, queue_length=5, throttle_rate_ms=100)  # Control message buffering and rate"
    )
)
def subscribe_for_duration(
    topic: str = "",
    msg_type: str = "",
    duration: float = 5.0,
    max_messages: int = 100,
    queue_length: Optional[int] = None,
    throttle_rate_ms: Optional[int] = None,
) -> dict:
    """
    Subscribe to a ROS topic via rosbridge for a fixed duration and collect messages.

    Args:
        topic (str): ROS topic name (e.g. "/cmd_vel", "/joint_states")
        msg_type (str): ROS message type (e.g. "geometry_msgs/Twist")
        duration (float): How long (seconds) to listen for messages
        max_messages (int): Maximum number of messages to collect before stopping
        queue_length (Optional[int]): How many messages to buffer before dropping old ones. Must be ≥ 1.
        throttle_rate_ms (Optional[int]): Minimum interval between messages in milliseconds. Must be ≥ 0.

    Returns:
        dict:
            {
                "topic": topic_name,
                "collected_count": N,
                "messages": [msg1, msg2, ...]
            }
    """
    # Validate critical args before subscribing
    if not topic or not msg_type:
        return {"error": "Missing required arguments: topic and msg_type must be provided."}

    # Validate optional parameters
    if queue_length is not None and (not isinstance(queue_length, int) or queue_length < 1):
        return {"error": "queue_length must be an integer ≥ 1"}

    if throttle_rate_ms is not None and (
        not isinstance(throttle_rate_ms, int) or throttle_rate_ms < 0
    ):
        return {"error": "throttle_rate_ms must be an integer ≥ 0"}

    # Send subscription request
    subscribe_msg: dict = {
        "op": "subscribe",
        "topic": topic,
        "type": msg_type,
    }

    # Add optional parameters if provided
    if queue_length is not None:
        subscribe_msg["queue_length"] = queue_length

    if throttle_rate_ms is not None:
        subscribe_msg["throttle_rate"] = throttle_rate_ms

    with ws_manager:
        send_error = ws_manager.send(subscribe_msg)
        if send_error:
            return {"error": f"Failed to subscribe: {send_error}"}

        collected_messages = []
        status_errors = []
        end_time = time.time() + duration

        # Loop until duration expires or we hit max_messages
        while time.time() < end_time and len(collected_messages) < max_messages:
            response = ws_manager.receive(timeout=0.5)  # non-blocking small timeout
            if response is None:
                continue  # idle timeout: no frame this tick

            msg_data = parse_json(response)
            if not msg_data:
                continue  # non-JSON or empty

            # Check for status errors from rosbridge
            if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                status_errors.append(msg_data.get("msg", "Unknown error"))
                continue

            # Check for published messages matching our topic
            if msg_data.get("op") == "publish" and msg_data.get("topic") == topic:
                collected_messages.append(msg_data.get("msg", {}))

        # Unsubscribe when done
        unsubscribe_msg = {"op": "unsubscribe", "topic": topic}
        ws_manager.send(unsubscribe_msg)

    return {
        "topic": topic,
        "collected_count": len(collected_messages),
        "messages": collected_messages,
        "status_errors": status_errors,  # Include any errors encountered during collection
    }


@mcp.tool(
    description=(
        "Publish a sequence of messages with delays.\n"
        "Example:\n"
        "publish_for_durations(topic='/cmd_vel', msg_type='geometry_msgs/msg/TwistStamped', messages=[{'linear': {'x': 1.0}}, {'linear': {'x': 0.0}}], durations=[1, 2])"
    )
)
def publish_for_durations(
    topic: str = "",
    msg_type: str = "",
    messages: List[Dict[str, Any]] = [],
    durations: List[float] = [],
) -> dict:
    """
    Publish a sequence of messages to a given ROS topic with delays in between.

    Args:
        topic (str): ROS topic name (e.g., "/cmd_vel")
        msg_type (str): ROS message type (e.g., "geometry_msgs/Twist")
        messages (List[Dict[str, Any]]): A list of message dictionaries (ROS-compatible payloads)
        durations (List[float]): A list of durations (seconds) to wait between messages

    Returns:
        dict:
            {
                "success": True,
                "published_count": <number of messages>,
                "topic": topic,
                "msg_type": msg_type
            }
            OR {"error": "<error message>"} if something failed
    """
    # Validate critical args before publishing
    if not topic or not msg_type or messages == [] or durations == []:
        return {
            "error": "Missing required arguments: topic, msg_type, messages, and durations must all be provided."
        }

    # Ensure same length for messages & durations
    if len(messages) != len(durations):
        return {"error": "messages and durations must have the same length"}

    # Use proper advertise → publish → unadvertise pattern
    with ws_manager:
        # 1. Advertise the topic
        advertise_msg = {"op": "advertise", "topic": topic, "type": msg_type}
        send_error = ws_manager.send(advertise_msg)
        if send_error:
            return {"error": f"Failed to advertise topic: {send_error}"}

        # Check for advertise response/errors
        response = ws_manager.receive(timeout=1.0)
        if response:
            try:
                msg_data = json.loads(response)
                if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                    return {"error": f"Advertise failed: {msg_data.get('msg', 'Unknown error')}"}
            except json.JSONDecodeError:
                pass  # Non-JSON response is usually fine for advertise

        published_count = 0
        errors = []

        # 2. Iterate and publish each message with a delay
        for i, (msg, delay) in enumerate(zip(messages, durations)):
            # Build the rosbridge publish message
            publish_msg = {"op": "publish", "topic": topic, "msg": msg}

            # Send it
            send_error = ws_manager.send(publish_msg)
            if send_error:
                errors.append(f"Message {i + 1}: {send_error}")
                continue  # Continue with next message instead of failing completely

            # Check for publish response/errors
            response = ws_manager.receive(timeout=1.0)
            if response:
                try:
                    msg_data = json.loads(response)
                    if msg_data.get("op") == "status" and msg_data.get("level") == "error":
                        errors.append(f"Message {i + 1}: {msg_data.get('msg', 'Unknown error')}")
                        continue
                except json.JSONDecodeError:
                    pass  # Non-JSON response is usually fine for publish

            published_count += 1

            # Wait before sending the next message
            time.sleep(delay)

        # 3. Unadvertise the topic
        unadvertise_msg = {"op": "unadvertise", "topic": topic}
        ws_manager.send(unadvertise_msg)

    return {
        "success": True,
        "published_count": published_count,
        "total_messages": len(messages),
        "topic": topic,
        "msg_type": msg_type,
        "errors": errors,  # Include any errors encountered during publishing
    }


@mcp.tool(description=("Get list of all currently running ROS nodes.\nExample:\nget_nodes()"))
def get_nodes() -> dict:
    """
    Get list of all currently running ROS nodes.

    Returns:
        dict: Contains list of all active nodes,
            or a message string if no nodes are found.
    """
    # rosbridge service call to get node list
    message = {
        "op": "call_service",
        "service": "/rosapi/nodes",
        "type": "rosapi/Nodes",
        "args": {},
        "id": "get_nodes_request_1",
    }

    # Request node list from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Return node info if present
    if response and "values" in response:
        nodes = response["values"].get("nodes", [])
        return {"nodes": nodes, "node_count": len(nodes)}
    else:
        return {"warning": "No nodes found"}


@mcp.tool(
    description=(
        "Get detailed information about a specific node including its publishers, subscribers, and services.\n"
        "Example:\n"
        "get_node_details('/turtlesim')"
    )
)
def get_node_details(node: str) -> dict:
    """
    Get detailed information about a specific node including its publishers, subscribers, and services.

    Args:
        node (str): The node name (e.g., '/turtlesim')

    Returns:
        dict: Contains detailed node information including publishers, subscribers, and services,
            or an error message if node doesn't exist.
    """
    # Validate input
    if not node or not node.strip():
        return {"error": "Node name cannot be empty"}

    result = {
        "node": node,
        "publishers": [],
        "subscribers": [],
        "services": [],
        "publisher_count": 0,
        "subscriber_count": 0,
        "service_count": 0,
    }

    # rosbridge service call to get node details
    message = {
        "op": "call_service",
        "service": "/rosapi/node_details",
        "type": "rosapi/NodeDetails",
        "args": {"node": node},
        "id": f"get_node_details_{node.replace('/', '_')}",
    }

    # Request node details from rosbridge
    with ws_manager:
        response = ws_manager.request(message)

    # Check for service response errors first
    if response and "result" in response and not response["result"]:
        # Service call failed - return error with details from values
        error_msg = response.get("values", {}).get("message", "Service call failed")
        return {"error": f"Service call failed: {error_msg}"}

    # Extract data from the response
    if response and "values" in response:
        values = response["values"]
        # Extract publishers, subscribers, and services from the response
        # Note: rosapi uses "publishing" and "subscribing" field names
        publishers = values.get("publishing", [])
        subscribers = values.get("subscribing", [])
        services = values.get("services", [])

        result["publishers"] = publishers
        result["subscribers"] = subscribers
        result["services"] = services
        result["publisher_count"] = len(publishers)
        result["subscriber_count"] = len(subscribers)
        result["service_count"] = len(services)

    # Check if we got any data
    if not result["publishers"] and not result["subscribers"] and not result["services"]:
        return {"error": f"Node {node} not found or has no details available"}

    return result


@mcp.tool(
    description=(
        "Get comprehensive information about all ROS nodes including their publishers, subscribers, and services.\n"
        "Example:\n"
        "inspect_all_nodes()"
    )
)
def inspect_all_nodes() -> dict:
    """
    Get comprehensive information about all ROS nodes including their publishers, subscribers, and services.

    Returns:
        dict: Contains detailed information about all nodes including:
            - Node names and details
            - Publishers for each node
            - Subscribers for each node
            - Services provided by each node
            - Connection counts and statistics
    """
    # First get all nodes
    nodes_message = {
        "op": "call_service",
        "service": "/rosapi/nodes",
        "type": "rosapi/Nodes",
        "args": {},
        "id": "inspect_all_nodes_request_1",
    }

    with ws_manager:
        nodes_response = ws_manager.request(nodes_message)

        if not nodes_response or "values" not in nodes_response:
            return {"error": "Failed to get nodes list"}

        nodes = nodes_response["values"].get("nodes", [])
        node_details = {}

        # Get details for each node
        node_errors = []
        for node in nodes:
            # Get node details (publishers, subscribers, services)
            node_details_message = {
                "op": "call_service",
                "service": "/rosapi/node_details",
                "type": "rosapi/NodeDetails",
                "args": {"node": node},
                "id": f"get_node_details_{node.replace('/', '_')}",
            }

            node_details_response = ws_manager.request(node_details_message)

            if node_details_response and "values" in node_details_response:
                values = node_details_response["values"]
                # Extract publishers, subscribers, and services from the response
                # Note: rosapi uses "publishing" and "subscribing" field names
                publishers = values.get("publishing", [])
                subscribers = values.get("subscribing", [])
                services = values.get("services", [])

                node_details[node] = {
                    "publishers": publishers,
                    "subscribers": subscribers,
                    "services": services,
                    "publisher_count": len(publishers),
                    "subscriber_count": len(subscribers),
                    "service_count": len(services),
                }
            elif (
                node_details_response
                and "result" in node_details_response
                and not node_details_response["result"]
            ):
                error_msg = node_details_response.get("values", {}).get(
                    "message", "Service call failed"
                )
                node_errors.append(f"Node {node}: {error_msg}")
            else:
                node_errors.append(f"Node {node}: Failed to get node details")

        return {
            "total_nodes": len(nodes),
            "nodes": node_details,
            "node_errors": node_errors,  # Include any errors encountered during inspection
        }


@mcp.tool(
    description=(
        "Get a single ROS parameter value by name.\nExample:\nget_param('/turtlesim:background_b')"
    )
)
def get_param(name: str) -> dict:
    """
    Get a single ROS parameter value by name.

    Args:
        name (str): The parameter name (e.g., '/turtlesim:background_b')

    Returns:
        dict: Contains parameter value and metadata, or error message if parameter not found.
    """
    if not name or not name.strip():
        return {"error": "Parameter name cannot be empty"}

    message = {
        "op": "call_service",
        "service": "/rosapi/get_param",
        "type": "rosapi/GetParam",
        "args": {"name": name},
        "id": f"get_param_{name.replace('/', '_').replace(':', '_')}",
    }

    with ws_manager:
        response = ws_manager.request(message)

    if response and "values" in response:
        result_data = response["values"]
        return {
            "name": name,
            "value": result_data.get("value", ""),
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        return {
            "name": name,
            "value": result_data.get("value", ""),
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to get parameter {name}: {error_msg}"}


@mcp.tool(
    description=(
        "Set a single ROS parameter value.\nExample:\nset_param('/turtlesim:background_b', '255')"
    )
)
def set_param(name: str, value: str) -> dict:
    """
    Set a single ROS parameter value.

    Args:
        name (str): The parameter name (e.g., '/turtlesim:background_b')
        value (str): The parameter value to set

    Returns:
        dict: Contains success status and metadata, or error message if failed.
    """
    if not name or not name.strip():
        return {"error": "Parameter name cannot be empty"}

    message = {
        "op": "call_service",
        "service": "/rosapi/set_param",
        "type": "rosapi/SetParam",
        "args": {"name": name, "value": value},
        "id": f"set_param_{name.replace('/', '_').replace(':', '_')}",
    }

    with ws_manager:
        response = ws_manager.request(message)

    if response and "values" in response:
        result_data = response["values"]
        return {
            "name": name,
            "value": value,
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        return {
            "name": name,
            "value": value,
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to set parameter {name}: {error_msg}"}


@mcp.tool(
    description=("Check if a ROS parameter exists.\nExample:\nhas_param('/turtlesim:background_b')")
)
def has_param(name: str) -> dict:
    """
    Check if a ROS parameter exists.

    Args:
        name (str): The parameter name (e.g., '/turtlesim:background_b')

    Returns:
        dict: Contains existence status and metadata, or error message if failed.
    """
    if not name or not name.strip():
        return {"error": "Parameter name cannot be empty"}

    message = {
        "op": "call_service",
        "service": "/rosapi/has_param",
        "type": "rosapi/HasParam",
        "args": {"name": name},
        "id": f"has_param_{name.replace('/', '_').replace(':', '_')}",
    }

    with ws_manager:
        response = ws_manager.request(message)

    if response and "values" in response:
        result_data = response["values"]
        return {
            "name": name,
            "exists": result_data.get("exists", False),
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        return {
            "name": name,
            "exists": result_data.get("exists", False),
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to check parameter {name}: {error_msg}"}


@mcp.tool(
    description=("Delete a ROS parameter.\nExample:\ndelete_param('/turtlesim:background_b')")
)
def delete_param(name: str) -> dict:
    """
    Delete a ROS parameter.

    Args:
        name (str): The parameter name (e.g., '/turtlesim:background_b')

    Returns:
        dict: Contains success status and metadata, or error message if failed.
    """
    if not name or not name.strip():
        return {"error": "Parameter name cannot be empty"}

    message = {
        "op": "call_service",
        "service": "/rosapi/delete_param",
        "type": "rosapi/DeleteParam",
        "args": {"name": name},
        "id": f"delete_param_{name.replace('/', '_').replace(':', '_')}",
    }

    with ws_manager:
        response = ws_manager.request(message)

    if response and "values" in response:
        result_data = response["values"]
        return {
            "name": name,
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        return {
            "name": name,
            "successful": result_data.get("successful", False),
            "reason": result_data.get("reason", ""),
        }
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to delete parameter {name}: {error_msg}"}


@mcp.tool(description=("Get list of all ROS parameter names.\nExample:\nget_parameters()"))
def get_parameters() -> dict:
    """
    Get list of all ROS parameter names.

    Returns:
        dict: Contains list of all parameter names, or error message if failed.
    """
    message = {
        "op": "call_service",
        "service": "/rosapi/get_param_names",
        "type": "rosapi/GetParamNames",
        "args": {},
        "id": "get_parameters_request_1",
    }

    with ws_manager:
        response = ws_manager.request(message)

    if response and "values" in response:
        names = response["values"].get("names", [])
        return {"parameters": names, "parameter_count": len(names)}
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        if isinstance(result_data, dict):
            names = result_data.get("names", [])
        else:
            names = []
        return {"parameters": names, "parameter_count": len(names)}
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to get parameter names: {error_msg}"}


@mcp.tool(
    description=(
        "Get detailed information about ROS parameters including types and values.\n"
        "Example:\n"
        "inspect_parameters('/turtlesim:background_b,/turtlesim:background_g')"
    )
)
def inspect_parameters(names: str) -> dict:
    """
    Get detailed information about ROS parameters including types and values.

    Args:
        names (str): Comma-separated parameter names to inspect

    Returns:
        dict: Contains detailed parameter information, or error message if failed.
    """
    if not names or not names.strip():
        return {"error": "At least one parameter name must be provided"}

    # Parse comma-separated parameter names
    param_names = [name.strip() for name in names.split(",") if name.strip()]
    if not param_names:
        return {"error": "No valid parameter names provided"}

    result = {"total_parameters": len(param_names), "parameters": {}, "parameter_errors": []}

    # Get details for each parameter using the working get_param function
    for param_name in param_names:
        try:
            # Use the working get_param function logic
            message = {
                "op": "call_service",
                "service": "/rosapi/get_param",
                "type": "rosapi/GetParam",
                "args": {"name": param_name},
                "id": f"get_param_{param_name.replace('/', '_').replace(':', '_')}",
            }

            with ws_manager:
                response = ws_manager.request(message)

            if response and "values" in response:
                result_data = response["values"]
                param_value = result_data.get("value", "")
                param_successful = result_data.get("successful", False)
            elif response and "result" in response and response["result"]:
                result_data = response["result"]
                param_value = result_data.get("value", "")
                param_successful = result_data.get("successful", False)
            else:
                result["parameter_errors"].append(f"Parameter {param_name}: Failed to get value")
                continue

            result["parameters"][param_name] = {
                "value": param_value,
                "type": "unknown",  # Type detection disabled for now
                "exists": param_successful,
            }

        except Exception as e:
            result["parameter_errors"].append(f"Parameter {param_name}: Exception - {str(e)}")
            continue

    return result


## ############################################################################################## ##
##
##                       NETWORK DIAGNOSTICS
##
## ############################################################################################## ##


@mcp.tool(
    description=(
        "Ping a robot's IP address and check if a specific port is open.\n"
        "A successful ping to the IP but not the port can indicate that ROSbridge is not running.\n"
        "Example:\n"
        "ping_robot(ip='192.168.1.100', port=9090)"
    )
)
def ping_robot(ip: str, port: int, ping_timeout: float = 2.0, port_timeout: float = 2.0) -> dict:
    """
    Ping an IP address and check if a specific port is open.

    Args:
        ip (str): The IP address to ping (e.g., '192.168.1.100')
        port (int): The port number to check (e.g., 9090)
        ping_timeout (float): Timeout for ping in seconds. Default = 2.0.
        port_timeout (float): Timeout for port check in seconds. Default = 2.0.

    Returns:
        dict: Contains ping and port check results with detailed status information.
    """
    return ping_ip_and_port(ip, port, ping_timeout, port_timeout)


## ############################################################################################## ##
##
##                      IMAGE ANALYSIS
##
## ############################################################################################## ##
@mcp.tool(
    description=(
        "First, subscribe to an Image topic using 'subscribe_once' to save an image.\n"
        "Then, use this tool to analyze the saved image\n"
    )
)
def analyze_previously_received_image():
    """
    Analyze the received image.

    This tool loads the previously saved image from './camera/received_image.jpeg'
    (which must have been created by 'parse_image' or 'subscribe_once'), and converts
    it into an MCP-compatible ImageContent format so that the LLM can interpret it.
    """
    path = "./camera/received_image.jpeg"
    if not os.path.exists(path):
        return {"error": "No previously received image found at ./camera/received_image.jpeg"}
    image = PILImage.open(path)
    return _encode_image_to_imagecontent(image)


def _encode_image_to_imagecontent(image):
    """
    Encodes a PIL Image to a format compatible with ImageContent.

    Args:
        image (PIL.Image.Image): The image to encode.

    Returns:
        ImageContent: JPEG-encoded image wrapped in an ImageContent object.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    img_obj = Image(data=img_bytes, format="jpeg")
    return img_obj.to_image_content()


def parse_arguments():
    """Parse command line arguments for MCP server configuration."""
    parser = argparse.ArgumentParser(
        description="ROS MCP Server - Connect to ROS robots via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                                    # Use stdio transport (default)
  python server.py --transport http --host 0.0.0.0 --port 9000
  python server.py --transport streamable-http --host 127.0.0.1 --port 8080
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http", "sse"],
        default="stdio",
        help="MCP transport protocol to use (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address for HTTP-based transports (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Port number for HTTP-based transports (default: 9000)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the MCP server console script."""
    # Parse command line arguments
    args = parse_arguments()

    # Update global variables with parsed arguments
    global MCP_TRANSPORT, MCP_HOST, MCP_PORT
    MCP_TRANSPORT = args.transport.lower()
    MCP_HOST = args.host
    MCP_PORT = args.port

    if MCP_TRANSPORT == "stdio":
        # stdio doesn't need host/port
        mcp.run(transport="stdio")

    elif MCP_TRANSPORT in {"http", "streamable-http"}:
        # http and streamable-http both require host/port
        print(f"Transport: {MCP_TRANSPORT} -> http://{MCP_HOST}:{MCP_PORT}")
        mcp.run(transport=MCP_TRANSPORT, host=MCP_HOST, port=MCP_PORT)

    elif MCP_TRANSPORT == "sse":
        print(f"Transport: {MCP_TRANSPORT} -> http://{MCP_HOST}:{MCP_PORT}")
        print("Currently unsupported. Use 'stdio', 'http', or 'streamable-http'.")
        mcp.run(transport=MCP_TRANSPORT, host=MCP_HOST, port=MCP_PORT)

    else:
        raise ValueError(
            f"Unsupported MCP_TRANSPORT={MCP_TRANSPORT!r}. "
            "Use 'stdio', 'http', or 'streamable-http'."
        )


if __name__ == "__main__":
    main()
