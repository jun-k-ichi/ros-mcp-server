# tools/ros_parameters.py
# Note: This module provides ROS parameter tools that will be imported by server.py
# The MCP instance and WebSocket manager are managed by server.py
# ws_manager will be passed as a parameter or imported when needed


def get_parameters(ws_manager) -> dict:
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


def get_param(name: str, ws_manager) -> dict:
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


def set_param(name: str, value: str, ws_manager) -> dict:
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


def has_param(name: str, ws_manager) -> dict:
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
            "successful": True,  # Service call was successful
            "reason": result_data.get("reason", ""),
        }
    elif response and "result" in response and response["result"]:
        result_data = response["result"]
        return {
            "name": name,
            "exists": result_data.get("exists", False),
            "successful": True,  # Service call was successful
            "reason": result_data.get("reason", ""),
        }
    else:
        error_msg = (
            response.get("values", {}).get("message", "Service call failed")
            if response
            else "No response"
        )
        return {"error": f"Failed to check parameter {name}: {error_msg}"}


def delete_param(name: str, ws_manager) -> dict:
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


def get_param_details(name: str, ws_manager) -> dict:
    """
    Get detailed information about a single ROS parameter including value, type, and metadata.

    Args:
        name (str): The parameter name (e.g., '/turtlesim:background_b')

    Returns:
        dict: Contains detailed parameter information, or error message if failed.
    """
    if not name or not name.strip():
        return {"error": "Parameter name cannot be empty"}

    result = {"total_parameters": 1, "parameters": {}, "parameter_errors": []}

    # Get details for the parameter using the working get_param function logic
    try:
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
            param_value = result_data.get("value", "")
            param_successful = result_data.get("successful", False)
        elif response and "result" in response and response["result"]:
            result_data = response["result"]
            param_value = result_data.get("value", "")
            param_successful = result_data.get("successful", False)
        else:
            result["parameter_errors"].append(f"Parameter {name}: Failed to get value")
            return result

        # Determine parameter type based on value
        param_type = "unknown"
        if param_successful and param_value:
            try:
                # Try to parse as different types
                if param_value.lower() in ["true", "false"]:
                    param_type = "bool"
                elif param_value.isdigit() or (param_value.startswith('-') and param_value[1:].isdigit()):
                    param_type = "int"
                elif param_value.replace('.', '', 1).isdigit() or (param_value.startswith('-') and param_value[1:].replace('.', '', 1).isdigit()):
                    param_type = "float"
                elif param_value.startswith('"') and param_value.endswith('"'):
                    param_type = "string"
                elif param_value.startswith('[') and param_value.endswith(']'):
                    param_type = "list"
                elif param_value.startswith('{') and param_value.endswith('}'):
                    param_type = "dict"
                else:
                    param_type = "string"  # Default to string
            except:
                param_type = "string"

        result["parameters"][name] = {
            "value": param_value,
            "type": param_type,
            "exists": param_successful,
        }

    except Exception as e:
        result["parameter_errors"].append(f"Parameter {name}: Exception - {str(e)}")

    return result


def register_parameters_tools(mcp_instance, ws_manager):
    """Register all ROS parameter tools with the MCP instance."""

    @mcp_instance.tool(
        description="Get list of all available ROS parameters.\nExample:\nget_parameters()"
    )
    def get_parameters_tool() -> dict:
        return get_parameters(ws_manager)

    @mcp_instance.tool(
        description="Get a single ROS parameter value by name.\nExample:\nget_param('/turtlesim:background_b')"
    )
    def get_param_tool(name: str) -> dict:
        return get_param(name, ws_manager)

    @mcp_instance.tool(
        description="Set a single ROS parameter value.\nExample:\nset_param('/turtlesim:background_b', '255')"
    )
    def set_param_tool(name: str, value: str) -> dict:
        return set_param(name, value, ws_manager)

    @mcp_instance.tool(
        description="Check if a ROS parameter exists.\nExample:\nhas_param('/turtlesim:background_b')"
    )
    def has_param_tool(name: str) -> dict:
        return has_param(name, ws_manager)

    @mcp_instance.tool(
        description="Delete a ROS parameter.\nExample:\ndelete_param('/turtlesim:background_b')"
    )
    def delete_param_tool(name: str) -> dict:
        return delete_param(name, ws_manager)

    @mcp_instance.tool(
        description="Get detailed information about a single ROS parameter including value, type, and metadata.\nExample:\nget_param_details('/turtlesim:background_b')"
    )
    def get_param_details_tool(name: str) -> dict:
        return get_param_details(name, ws_manager)