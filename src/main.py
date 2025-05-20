"""
MCP Server to use Namecheap to change DNS servers for existing domains
"""

import os
import json
import argparse
from typing import Dict, List, Any, Union
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from namecheap import Namecheap

load_dotenv()

namecheap = Namecheap(
    api_key=os.getenv('API_KEY'),
    username=os.getenv('USERNAME'),
    client_ip=os.getenv('CLIENT_IP'),
    sandbox=os.getenv('SANDBOX', 'true').lower() == 'true'
)

# Create an MCP server
mcp = FastMCP("Namecheap")

@mcp.tool(
    annotations={
        "title": "Set Default DNS",
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def set_default_dns(domain_name: str) -> Dict[str, Any]:
    """Sets domain to use Namecheap's default DNS servers"""
    result = namecheap.set_default_dns(
        domain_name=domain_name
    )
    return {'success': result, 'message': 'Default DNS servers set successfully'}


@mcp.tool(
    annotations={
        "title": "Set Custom DNS",
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def set_custom_dns(domain_name: str, nameservers: List[str]) -> Dict[str, Any]:
    """Sets domain to use custom DNS servers"""
    result = namecheap.set_custom_dns(
        domain_name=domain_name,
        nameservers=nameservers
    )
    return {'success': result, 'message': 'Custom DNS servers set successfully'}


@mcp.tool(
    annotations={
        "title": "Get DNS List",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_dns_list(domain_name: str) -> Dict[str, Any]:
    """Gets a list of DNS servers associated with the specified domain"""
    result = namecheap.get_dns_list(
        domain_name=domain_name
    )
    return {'dns_servers': result}


@mcp.tool(
    annotations={
        "title": "Get Hosts",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_hosts(domain_name: str) -> Dict[str, Any]:
    """Retrieves DNS host record settings for the specified domain"""
    result = namecheap.get_hosts(
        domain_name=domain_name
    )
    return {'hosts': result}


@mcp.tool(
    annotations={
        "title": "Get Email Forwarding",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_email_forwarding(domain_name: str) -> Dict[str, Any]:
    """Gets email forwarding settings for the specified domain"""
    result = namecheap.get_email_forwarding(
        domain_name=domain_name
    )
    return {'email_forwarding': result}


@mcp.tool(
    annotations={
        "title": "Set Email Forwarding",
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def set_email_forwarding(domain_name: str, forwards: List[Dict[str, str]]) -> Dict[str, Any]:
    """Sets email forwarding for the specified domain"""
    result = namecheap.set_email_forwarding(
        domain_name=domain_name,
        forwards=forwards
    )
    return {'success': result, 'message': 'Email forwarding set successfully'}


@mcp.tool(
    annotations={
        "title": "Get Domains",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_domains() -> Dict[str, Any]:
    """Gets a list of domains in the user's account"""
    result = namecheap.get_domains()
    return {'domains': result}

@mcp.tool(
    annotations={
        "title": "Get Domain",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_domain_info(domain_name: str) -> Dict[str, Any]:
    """Gets a domain in the user's account"""
    result = namecheap.get_domain_info(
        domain_name=domain_name
    )
    return {'domain_info': result}

@mcp.tool(
    annotations={
        "title": "Check domains for availability",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def check_domains_availability(domains: Union[str, List[str]], suggestions: bool = False) -> Dict[str, Any]:
    """Checks the availability of one or multiple domain names"""
    result = namecheap.check_domains_availability(
        domains=domains,
        suggestions=suggestions
    )
    return {'domains_availability': result}

@mcp.tool(
    annotations={
        "title": "Set DNS Host Records",
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def set_hosts(domain_name: str, hosts: List[Dict[str, str]]) -> Dict[str, Any]:
    """Sets DNS host records for the specified domain"""
    result = namecheap.set_hosts(
        domain_name=domain_name,
        hosts=hosts
    )
    return {'success': result, 'message': 'Host records set successfully'}

@mcp.tool(
    annotations={
        "title": "Add DNS Host Record",
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def add_host(domain_name: str, hosts: List[Dict[str, str]]) -> Dict[str, Any]:
    """Adds a new domain to Namecheap"""
    get_hosts = namecheap.get_hosts(
        domain_name=domain_name
    )
    existing_hosts = get_hosts['Hosts']
    hosts.extend(existing_hosts)
    
    result = namecheap.set_hosts(
        domain_name=domain_name,
        hosts=hosts
    )
    return {'success': result, 'message': 'Host added successfully'}

def main():
    """Entry point for the namecheap-mcp command-line tool"""
    parser = argparse.ArgumentParser(description='Run the Namecheap MCP Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind the server to')
    parser.add_argument('--test', action='store_true', help='Run a test without starting the server')
    parser.add_argument('--stdio', action='store_true', help='Run in stdio mode for Windsurf integration')
    
    args = parser.parse_args()
    
    if args.test:
        # Run a test request
        print("\nRunning test request for get_hosts...")
        result = get_hosts(domain_name="example.com")
        print(json.dumps(result, indent=2))
    else:
        # Start the MCP server
        if args.stdio:
            # Run in stdio mode for Windsurf integration
            mcp.run_stdio()
        else:
            # Run in HTTP mode
            mcp.run_http(host=args.host, port=args.port)


# Example of how to use the MCP service
if __name__ == "__main__":
    main()