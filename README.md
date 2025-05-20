# Namecheap MCP Service

This is a Model Context Protocol (MCP) service for interacting with the Namecheap API, specifically focusing on DNS-related operations.

## Overview

The Namecheap MCP service provides a standardized interface for AI models to interact with the Namecheap API. It allows for managing DNS settings, email forwarding, and host records for domains registered with Namecheap.

## Features

- Set domains to use Namecheap's default DNS servers
- Set domains to use custom DNS servers
- Get a list of DNS servers for a domain
- Get and set host records for a domain
- Get and set email forwarding settings for a domain

## Setup

1. Clone this repository
2. Install the required dependencies using `uv`:
   ```bash
   # Install uv if you don't have it already
   curl -sSf https://install.determinate.systems/uv | sh
   
   # Create a virtual environment and install dependencies
   uv venv
   uv pip install -e .
   ```
3. Create a `.env` file with your Namecheap API credentials:
   ```
   SANDBOX=false  # Set to true for testing
   API_KEY=your_api_key
   USERNAME=your_username
   CLIENT_IP=your_client_ip
   ```

## Usage

### Running the MCP Server

Run the MCP server using the provided script:

```
python run_mcp_server.py
```

### Available Functions

The service exposes the following functions:

- `set_default_dns`: Sets domain to use Namecheap's default DNS servers
- `set_custom_dns`: Sets domain to use custom DNS servers
- `get_dns_list`: Gets a list of DNS servers for a domain
- `get_hosts`: Gets host records for a domain
- `set_hosts`: Sets host records for a domain
- `get_email_forwarding`: Gets email forwarding settings for a domain
- `set_email_forwarding`: Sets email forwarding for a domain

### Testing Locally

You can test the MCP service locally before integrating with Windsurf:

1. Start the MCP server:
   ```bash
   python src/main.py
   ```

2. In another terminal, you can test the API endpoints using curl:
   ```bash
   # Get available functions
   curl http://127.0.0.1:5000/functions
   
   # Call a function
   curl -X POST http://127.0.0.1:5000/call \
     -H "Content-Type: application/json" \
     -d '{"function": "get_dns_list", "params": {"domain_name": "example.com"}}'
   ```

3. Or use the test mode to see example output without starting the server:
   ```bash
   python src/main.py --test
   ```

### Example Usage with an MCP Client

```python
# Example of how an MCP client might use this service
result = mcp_client.call("namecheap", "get_dns_list", {"domain_name": "example.com"})
print(result)
```

## MCP Configuration

The `mcp_config.json` file contains the configuration for the MCP service, including:

- Service name and description
- Server configuration (path to the main module, class name, etc.)
- Authentication settings (currently set to "none")

### Using with Windsurf

To use this MCP service with Windsurf, add the following configuration to your Windsurf MCP config file (typically located at `~/.codeium/windsurf/mcp_config.json`):

```json
"mcpServers": {
  "Namecheap": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "namecheap-mcp/src/main.py"
      ]
   }
}
```

Make sure to:

1. Update the path in the `args` array to point to your `main.py` file
2. Adjust the `PATH` and `SHELL` environment variables as needed for your system

After configuring the MCP service in Windsurf, you can interact with the Namecheap API using natural language. For example:

- "Get the DNS records for example.com"
- "Set example.com to use Namecheap's default DNS servers"
- "Update the host records for example.com"

## File Structure

- `src/main.py`: Main MCP service implementation
- `src/namecheap.py`: Namecheap API client implementation
- `mcp_config.json`: MCP service configuration
- `run_mcp_server.py`: Script to run the MCP server
- `.env`: Environment variables for API credentials

## License

This project is licensed under the MIT License - see the LICENSE file for details.
