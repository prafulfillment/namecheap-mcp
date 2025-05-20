# Namecheap MCP Service

This is a Model Context Protocol (MCP) service for interacting with the Namecheap API, specifically focusing on DNS-related operations.

## Overview

The Namecheap MCP service provides a standardized interface for AI models to interact with the Namecheap API. It allows for managing DNS settings, email forwarding, and host records for domains registered with Namecheap.

## Setup

1. Clone this repository
2. Create a `.env` file with your Namecheap API credentials:
   ```
   SANDBOX=false  # Set to true for testing
   API_KEY=your_api_key
   USERNAME=your_username
   CLIENT_IP=your_client_ip
   ```

## Usage

### Available Functions

The service exposes the following functions:

- `set_default_dns`: Sets domain to use Namecheap's default DNS servers
- `set_custom_dns`: Sets domain to use custom DNS servers
- `get_dns_list`: Gets a list of DNS servers for a domain
- `get_hosts`: Gets host records for a domain
- `set_hosts`: Sets host records for a domain
- `get_email_forwarding`: Gets email forwarding settings for a domain
- `set_email_forwarding`: Sets email forwarding for a domain

### Using with AI Code Editor

To use this MCP service with your code editor, add the following configuration to your code editor's MCP config file (typically located at `~/.codeium/windsurf/mcp_config.json`):

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

After configuring the MCP service in your code editor, you can interact with the Namecheap API using natural language. For example:

- "Get the DNS records for example.com"
- "Set example.com to use Namecheap's default DNS servers"
- "Update the host records for example.com"