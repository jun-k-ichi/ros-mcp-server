# ChatGPT Desktop with ROS-MCP-Server

## Prerequisites

### Prepare host machine (MCP Server)

* Installation of ChatGPT Desktop. Download [here](chatgpt.com/download) or Microsoft Store.
* Installation of WSL (Linux).

### Prepare target robot (ROS)

* Installation of Ubuntu or WSL (Windows Subsystem for Linux).
* Installation of ROS or ROS2. Test if ROS is installed by running Turtlesim. If you are not sure, follow, this toturial \[https://wiki.ros.org/ROS/Tutorials]

# Tutorial

## Quick Start (For Experienced Users)

1. **Install dependencies**: `curl -LsSf https://astral.sh/uv/install.sh | sh` and `ngrok config add-authtoken <YOUR_AUTHTOKEN>`
2. **Clone repository**: `cd ~ && git clone https://github.com/robotmcp/ros-mcp-server.git && cd ros-mcp-server`
3. **Start MCP server**: `uv run server.py --transport streamable-http --host 127.0.0.1 --port 9000`
4. **Start ngrok tunnel**: `ngrok http --url=your-domain.ngrok-free.app 9000`
5. **Configure ChatGPT**: Add connector with URL `https://your-domain.ngrok-free.app/mcp`
6. **Start ROS**: `ros2 launch rosbridge_server rosbridge_websocket_launch.xml & ros2 run turtlesim turtlesim_node`
7. **Test**: Ask ChatGPT to "List ROS topics"

## 1.1 Installation on Host Machine

### Install dependencies

* Install [`uv`](https://github.com/astral-sh/uv) using one of the following methods:

    <details>
	<summary><strong>Option A: PowerShell (Windows)</strong></summary>

	```bash
	winget install --id=astral-sh.uv -e
	```
	or
	```bash
	pip install uv
	```
	
	</details>

 	<details>
	<summary><strong>Option B: WSL (Linux) </strong></summary>

	```bash
	curl -LsSf https://astral.sh/uv/install.sh | sh
	```
	or (not recommended)
	```bash
	pip install uv
	```
	or (not recommended)
	```bash
	sudo snap install --classic astral-uv
	```
	</details>

* Install [`ngrok`](https://dashboard.ngrok.com/get-started/setup/linux) using one of the following methods:
	
	<details>
 	<summary><strong>Option A: PowerShell (Windows)</strong></summary>
	
	Install from Microsoft Store or from [here](https://dashboard.ngrok.com/get-started/setup/windows)
    </details>

	<details>
	<summary><strong>Option B: WSL (Linux)</strong></summary>
	
	Using Apt:
	
	```bash
	curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \\
	  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \\
	  \&\& echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \\
	  | sudo tee /etc/apt/sources.list.d/ngrok.list \\
	  \&\& sudo apt update \\
	  \&\& sudo apt install ngrok
	```
	or snap:
	```bash
	sudo snap install ngrok
	```
	</details>

* Login or create your account at [`ngrok`](https://dashboard.ngrok.com/login)
* Navigate to [`Your Authtoken`](https://dashboard.ngrok.com/get-started/your-authtoken)
* Copy your `Authtoken` to clipboard `<YOUR_AUTHTOKEN>`
* Activate `ngrok` with the following command, replacing `<YOUR_AUTHTOKEN>`:

```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
```
* Obtain a static domain in `ngrok` by navigating to [Domains](https://dashboard.ngrok.com/domains)
* It should look be something like: `abc123-xyz789.ngrok-free.app`
* Save the ROS-MCP url domain, replacing it with yours.

	<details>
	<summary><strong>Option A: PowerShell (Windows)</strong></summary>

	```bash
	$env:MCP_DOMAIN=abc123-xyz789.ngrok-free.app
	```
	</details>

	<details>
	<summary><strong>Option B: WSL (Linux)</strong></summary>

	```bash
	export MCP_DOMAIN=abc123-xyz789.ngrok-free.app
	```
	</details>

* In WSL (Linux), consider adding your ngrok domain to `.bashrc` for convenience

```bash
export MCP_DOMAIN=your-domain.ngrok-free.app
```

### Install ROS-MCP Server

*  On your Host Machine, clone the repository and navigate to the ROS-MCP Server folder.

```bash 
cd ~
git clone https://github.com/robotmcp/ros-mcp-server.git
cd ros-mcp-server
```


## 1.2 Run ROS-MCP Server

* Run the ROS-MCP using one of the following:
		
	<details>
	<summary><strong>Option A: PowerShell (Windows)</strong></summary>

	If you installed `uv` use the following:
	```bash
	uv run server.py --transport streamable-http --host 127.0.0.1 --port 9000
	```
	
	Otherwise you have to install all the dependencies manually and run:

	```bash
	python server.py --transport streamable-http --host 127.0.0.1 --port 9000
	```
	
	</details>

	<details>
	<summary><strong>Option B: WSL (Linux)</strong></summary>

	Open WSL and run the following:
	```bash
	uv run server.py --transport streamable-http --host 127.0.0.1 --port 9000
	```

	or use the launch script (which will be updated to use command-line arguments):

	```bash
	cd scripts
	launch_mcp_server.sh
	```
	</details>

* The server will start at `127.0.0.1:9000` by default. You can customize the host and port using the `--host` and `--port` arguments.



## 1.3 Tunnel ROS-MCP Server 

* On your host machine, launch `ngrok` with one of the following:

  	<details>
	<summary><strong>Option A: PowerShell (Windows)</strong></summary>

	In PowerShell, set your ngrok domain:
	
	```bash
	$env:MCP_DOMAIN=<YOUR_DOMAIN>
	```
	Run `ngrok` to tunnel your ROS-MCP server.
	
	```bash
	ngrok http --url=$env:MCP_DOMAIN 9000
	```
	</details>

	<details>
	<summary><strong>Option B: WSL (Linux)</strong></summary>

	In WSL, set your ngrok domain:
	```bash
	export MCP_DOMAIN=<YOUR_DOMAIN>
	```
 	Run `ngrok` to tunnel your ROS-MCP server.
	```bash
	ngrok http --url=${MCP_DOMAIN} 9000
	```
	Or you can also launch:
	```bash
	launch_mcp_tunnel_.sh
	```
 	</details>

* Once you launch `ngrok`, verify your public url domain, it should be the same as `MCP_DOMAIN`.

	```bash
	https://your-domain.ngrok-free.app -> http://localhost:9000
	```


## 1.4 Connect ROS-MCP to ChatGPT

* Open ChatGPT Desktop
* Navigate to Settings (Bottom Left)
* Open Connectors
* Create and fill the following:

	- Name: *ROS-MCP Server*
	- Description: *An MCP Server to connect with ROS/ROS2*
	- MCP Server URL: `https://your-domain.ngrok-free.app/mcp` (don't forget to replace with your domain and add the `/mcp`)
	- Authentication: *No authentication*
	- I trust this application

* In ChatGPT, start a new Chat, navigate to `+` > `Developer Mode` > `Add sources` > Activate `ROS-MCP Server`

## 1.5 Run ROS on Target Machine

In WSL, launch `rosbridge` and `turtlesim`

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml & ros2 run turtlesim turtlesim_node
```

or

```bash
launch_ros.sh
```

## 1.6 Test Your Setup

Once everything is configured, test your connection:

1. **Start a new chat in ChatGPT Desktop**
2. **Activate the ROS-MCP Server** in Developer Mode
3. **Try a simple ROS command** like:
   - "List all available ROS topics"
   - "Show me the current ROS node information"
   - "What robots are available in the specifications?"

4. **Verify the connection** - you should see ROS-related responses from the MCP server

## 2. Troubleshooting

### Common Issues

**MCP Server not connecting:**
- Verify the server is running: Check if `uv run server.py` is active
- Check if ngrok tunnel is working: Visit your ngrok URL in browser
- Ensure the server is accessible at `http://127.0.0.1:9000/mcp`

**ROS Bridge connection failed:**
- Make sure ROS is running: `ros2 node list`
- Verify rosbridge is active: `ros2 launch rosbridge_server rosbridge_websocket_launch.xml`
- Check if port 9090 is available

**Ngrok tunnel issues:**
- Verify your authtoken is set: `ngrok config check`
- Check if your domain is active: Visit ngrok dashboard at `http://127.0.0.1:4040/status`
- Ensure port 9000 is not blocked by firewall

**ChatGPT connector not working:**
- Verify the MCP Server URL includes `/mcp` at the end
- Check if "I trust this application" is checked
- Restart ChatGPT Desktop after adding the connector

### Debug Commands

```bash
# Test server locally
curl http://127.0.0.1:9000/mcp

# Test ngrok tunnel
curl https://your-domain.ngrok-free.app/mcp

# Test ROS installation
wsl -- ros2 node list

# Test rosbridge
wsl -- ros2 topic list

# Check ngrok status
ngrok api tunnels list
```

## 3. Usage Examples

Once connected, you can use natural language to interact with your ROS system:

- **"Move the turtle forward"** - Controls turtlesim
- **"What topics are currently publishing?"** - Lists active topics
- **"Show me the robot specifications"** - Displays available robot configs
- **"Connect to robot at IP 192.168.1.100"** - Connects to remote robot
- **"Take a picture with the camera"** - Captures camera data
- **"Publish a velocity command"** - Sends movement commands

## 4. Advanced Configuration

### Command-line Arguments

You can customize the MCP server behavior with command-line arguments:

```bash
# Show all available options
python server.py --help

# Different transport options
python server.py --transport stdio                    # Default: stdio
python server.py --transport http --host 0.0.0.0 --port 9000
python server.py --transport streamable-http --host 127.0.0.1 --port 9000

# Custom host and port
python server.py --transport streamable-http --host 0.0.0.0 --port 8080
```

### Environment Variables (for ngrok)

You can still use environment variables for ngrok configuration:

```bash
# Ngrok settings
export MCP_DOMAIN="your-domain.ngrok-free.app"  # Your ngrok domain
```

## 5. FAQ

**Q: Do I need ngrok for local testing?**
A: For ChatGPT Desktop, yes. ChatGPT requires a public URL to connect to MCP servers.

**Q: Can I use a different tunneling service?**
A: Yes, you can use any tunneling service that provides HTTPS URLs, but ngrok is recommended.

**Q: Is the connection secure?**
A: The connection uses HTTPS through ngrok, but for production use, consider additional security measures.

**Q: Can I run multiple MCP servers?**
A: Yes, you can configure multiple servers, but each needs its own ngrok tunnel and port.

**Q: What if my ngrok domain changes?**
A: You'll need to update the MCP Server URL in ChatGPT Desktop settings.

**Q: Can I use this without WSL?**
A: The current setup requires WSL for ROS compatibility on Windows. Linux and macOS users can run directly.

## 6. Tested Configurations

### Host Machine
* Windows 11
* WSL with Ubuntu 22.04
* ChatGPT Desktop
* ngrok (free/paid)

### Target Machine
* WSL with Ubuntu 22.04
* ROS 2 Jazzy
* rosbridge_server

## 7. Support and Contributing

### Getting Help
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/robotmcp/ros-mcp-server/issues)
- **Documentation**: Check the main [README.md](../../README.md) for additional information
- **Community**: Join discussions in the project's GitHub Discussions

### Contributing
We welcome contributions! Please see our [Contributing Guide](../../docs/contributing.md) for details on:
- Setting up a development environment
- Code style guidelines
- Submitting pull requests
- Testing procedures