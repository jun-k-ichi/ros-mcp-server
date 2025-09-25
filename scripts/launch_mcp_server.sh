#!/usr/bin/env bash
set -eo pipefail

# Colors for log output
BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting MCP server environment...${NC}"

# 0. Set default transport protocol for the MCP server
MCP_TRANSPORT="streamable-http"
MCP_HOST="127.0.0.1"
MCP_PORT="9000"

# 1. Check if MCP server is running
if pgrep -f ros-mcp-server > /dev/null; then
  echo -e "${YELLOW}[mcp-server]${NC} is already running. Continuing without starting a new instance."
  MCP_PID=$(pgrep -f ros-mcp-server | head -n1)
else 
  # 2. Start MCP server
  echo -e "${GREEN}[mcp-server]${NC} Launching MCP server..."
  # Run with uv using command-line arguments
  uv run ../server.py --transport "$MCP_TRANSPORT" --host "$MCP_HOST" --port "$MCP_PORT" &
  MCP_PID=$!
fi

echo -e "${GREEN}[mcp-server]${NC} mcp-server PID:  $MCP_PID"

# 3. Trap to clean up processes on exit
trap "echo -e '${GREEN}[mcp-server] ${NC}Stopping MCP processes...'; kill -9 $MCP_PID" SIGINT SIGTERM

# 4. Keep script running, showing logs
wait
