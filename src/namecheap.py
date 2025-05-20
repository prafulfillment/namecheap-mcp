"""
Namecheap MCP (Model Context Protocol) Implementation

This module provides a Model Context Protocol implementation for the Namecheap API,
specifically focusing on DNS-related methods.

Methods implemented:
- setDefault: Sets DNS servers to default Namecheap DNS servers
- setCustom: Sets DNS servers to custom DNS servers
- getList: Gets a list of DNS servers for the specified domain
- getHosts: Gets a list of host records for the specified domain
- getEmailForwarding: Gets a list of email forwarding settings for the specified domain
- setEmailForwarding: Sets email forwarding for the specified domain
- setHosts: Sets host records for the specified domain
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from models import EmailForward, HostRecord
from utils import extract_domain_parts


class Namecheap:
    """
    Namecheap Model Context Protocol Implementation
    
    This class provides an interface to interact with the Namecheap API,
    specifically for DNS-related operations.
    """
    
    # Define the XML namespace for Namecheap API responses
    NAMESPACE = {'nc': 'http://api.namecheap.com/xml.response'}
    
    def __init__(self, api_key: str, username: str, client_ip: str, sandbox: bool = False):
        """
        Initialize the Namecheap MCP.
        
        Args:
            api_key: Your Namecheap API key
            username: Your Namecheap username
            client_ip: IP address of the client making the request
            sandbox: Whether to use the sandbox environment (default: False)
        """
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        
        if sandbox:
            self.base_url = "https://api.sandbox.namecheap.com/xml.response"
        else:
            self.base_url = "https://api.namecheap.com/xml.response"
            
        self.common_params = {
            'ApiUser': username ,
            'ApiKey': api_key,
            'UserName': username,
            'ClientIp': client_ip
        }
    
    def _make_request(self, command: str, params: Dict[str, str]) -> ET.Element:
        """
        Make a request to the Namecheap API.
        
        Args:
            command: The API command to execute
            params: Additional parameters for the request
            
        Returns:
            ElementTree root element containing the response
        
        Raises:
            Exception: If the API returns an error with error number and message
        """
        # Combine common parameters with request-specific parameters
        request_params = {**self.common_params, 'Command': command, **params}
        
        # Make the request
        response = requests.post(self.base_url, params=request_params)
        
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Check for errors
        status = root.attrib.get('Status')
        
        if status == 'ERROR':
            # Find the Error element using the namespace
            errors = root.findall('.//nc:Error', self.NAMESPACE)
            
            if errors:
                error = errors[0]
                error_number = error.attrib.get('Number', 'Unknown')
                error_message = error.text or 'Unknown error'
                raise Exception(f"Namecheap API Error {error_number}: {error_message}")
            else:
                raise Exception("Unknown Namecheap API Error")
                
        return root
    
    def _parse_host_records(self, root: ET.Element) -> List[Dict[str, str]]:
        """
        Parse host records from the API response.
        
        Args:
            root: ElementTree root element containing the response
            
        Returns:
            List of host records
        """
        hosts = []
        host_elements = root.findall('.//nc:host', self.NAMESPACE)
        
        for host in host_elements:
            host_data = {
                'HostId': host.attrib.get('HostId', ''),
                'Name': host.attrib.get('Name', ''),
                'Type': host.attrib.get('Type', ''),
                'Address': host.attrib.get('Address', ''),
                'MXPref': host.attrib.get('MXPref', ''),
                'TTL': host.attrib.get('TTL', '')
            }
            hosts.append(host_data)
            
        return hosts
    
    def _parse_email_forwarding(self, root: ET.Element) -> List[Dict[str, str]]:
        """
        Parse email forwarding records from the API response.
        
        Args:
            root: ElementTree root element containing the response
            
        Returns:
            List of email forwarding records
        """
        forwards = []
        forward_elements = root.findall('.//nc:forward', self.NAMESPACE)
        
        for forward in forward_elements:
            forward_data = {
                'MailBox': forward.attrib.get('MailBox', ''),
                'ForwardTo': forward.attrib.get('ForwardTo', '')
            }
            forwards.append(forward_data)
            
        return forwards
    
    def set_default(self, domain_name: str) -> Dict[str, Any]:
        """
        Sets domain to use Namecheap's default DNS servers.
        
        Args:
            domain_name: The domain name
            
        Returns:
            Dictionary containing the API response
        """
        sld, tld = extract_domain_parts(domain_name)
        
        params = {
            'SLD': sld,
            'TLD': tld
        }
        
        root = self._make_request('namecheap.domains.dns.setDefault', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSSetDefaultResult', self.NAMESPACE)
        if result is not None:
            return {
                'Domain': result.attrib.get('Domain', ''),
                'Updated': result.attrib.get('Updated', '').lower() == 'true'
            }
        
        return {'Updated': False}
    
    def set_custom(self, domain_name: str, nameservers: List[str]) -> Dict[str, Any]:
        """
        Sets domain to use custom DNS servers.
        
        Args:
            domain_name: The domain name
            nameservers: List of nameservers (up to 12)
            
        Returns:
            Dictionary containing the API response
        """
        sld, tld = extract_domain_parts(domain_name)
        
        if len(nameservers) > 12:
            raise ValueError("Maximum of 12 nameservers allowed")
            
        # Join nameservers with comma
        nameservers_str = ','.join(nameservers)
        
        params = {
            'SLD': sld,
            'TLD': tld,
            'Nameservers': nameservers_str
        }
        
        root = self._make_request('namecheap.domains.dns.setCustom', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSSetCustomResult', self.NAMESPACE)
        if result is not None:
            return {
                'Domain': result.attrib.get('Domain', ''),
                'Updated': result.attrib.get('Updated', '').lower() == 'true'
            }
        
        return {'Updated': False}
    
    def get_dns_list(self, domain_name: str) -> Dict[str, Any]:
        """
        Gets a list of DNS servers associated with the specified domain.
        
        Args:
            domain_name: The domain name
            
        Returns:
            Dictionary containing the API response with nameservers
        """
        sld, tld = extract_domain_parts(domain_name)
        
        params = {
            'SLD': sld,
            'TLD': tld
        }
        
        root = self._make_request('namecheap.domains.dns.getList', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSGetListResult', self.NAMESPACE)
        nameservers = []
        
        if result is not None:
            for ns in result.findall('.//nc:Nameserver', self.NAMESPACE):
                if ns.text:
                    nameservers.append(ns.text)
                    
            return {
                'Domain': result.attrib.get('Domain', ''),
                'IsUsingOurDNS': result.attrib.get('IsUsingOurDNS', '').lower() == 'true',
                'Nameservers': nameservers
            }
        
        return {'Nameservers': []}
    
    def get_hosts(self, domain_name: str) -> Dict[str, Any]:
        """
        Retrieves DNS host record settings for the specified domain.
        
        Args:
            domain_name: The domain name
            
        Returns:
            Dictionary containing the API response with host records
        """
        sld, tld = extract_domain_parts(domain_name)
        
        params = {
            'SLD': sld,
            'TLD': tld
        }
        
        root = self._make_request('namecheap.domains.dns.getHosts', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSGetHostsResult', self.NAMESPACE)
        
        if result is not None:
            hosts = self._parse_host_records(result)
            
            return {
                'Domain': result.attrib.get('Domain', ''),
                'IsUsingOurDNS': result.attrib.get('IsUsingOurDNS', '').lower() == 'true',
                'Hosts': hosts
            }
        
        return {'Hosts': []}
    
    def get_email_forwarding(self, domain_name: str) -> Dict[str, Any]:
        """
        Gets email forwarding settings for the specified domain.
        
        Args:
            domain_name: The domain name
            
        Returns:
            Dictionary containing the API response with email forwarding records
        """
        params = {
            'DomainName': domain_name,
        }
        
        root = self._make_request('namecheap.domains.dns.getEmailForwarding', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSGetEmailForwardingResult', self.NAMESPACE)
        
        if result is not None:
            forwards = self._parse_email_forwarding(result)
            
            return {
                'Domain': result.attrib.get('Domain', ''),
                'EmailForwarding': forwards
            }
        
        return {'EmailForwarding': []}
    
    def set_email_forwarding(self, domain_name: str, forwards: List[EmailForward]) -> Dict[str, Any]:
        """
        Sets email forwarding for the specified domain.
        
        Args:
            domain_name: The domain name
            forwards: List of EmailForward objects representing email forwarding records
            
        Returns:
            Dictionary containing the API response
        """        
        params = {
            'DomainName': domain_name,
        }
        
        # Add forwarding records
        for i, forward in enumerate(forwards):
            params[f'MailBox{i+1}'] = forward.mailbox
            params[f'ForwardTo{i+1}'] = forward.forward_to
        
        root = self._make_request('namecheap.domains.dns.setEmailForwarding', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSSetEmailForwardingResult', self.NAMESPACE)
        
        if result is not None:
            return {
                'Domain': result.attrib.get('Domain', ''),
                'IsSuccess': result.attrib.get('IsSuccess', '').lower() == 'true'
            }
        
        return {'IsSuccess': False}
    
    def set_hosts(self, domain_name: str, hosts: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Sets DNS host records for the specified domain.
        
        Args:
            domain_name: The domain name
            hosts: List of HostRecord objects representing DNS host records
            
        Returns:
            Dictionary containing the API response
        """
        sld, tld = extract_domain_parts(domain_name)
        
        params = {
            'SLD': sld,
            'TLD': tld
        }
        
        # Add host records
        for i, host in enumerate(hosts):
            params[f'HostName{i+1}'] = host['Name']
            params[f'RecordType{i+1}'] = host['Type']
            params[f'Address{i+1}'] = host['Address']
            
            # Optional parameters
            if host['Type'] == 'MX':
                params[f'MXPref{i+1}'] = host['MXPref']
                params['EmailType'] = 'MX'
            
            params[f'TTL{i+1}'] = host['TTL']
        
        root = self._make_request('namecheap.domains.dns.setHosts', params)
        
        # Parse the response
        result = root.find('.//nc:DomainDNSSetHostsResult', self.NAMESPACE)
        
        if result is not None:
            return {
                'Domain': result.attrib.get('Domain', ''),
                'IsSuccess': result.attrib.get('IsSuccess', '').lower() == 'true',
                'Hosts': self._parse_host_records(result) if result.findall('.//host') else []
            }
        
        return {'IsSuccess': False, 'Hosts': []}