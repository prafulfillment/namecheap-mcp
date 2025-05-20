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
from typing import Dict, List, Any, Union
from models import EmailForward
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
    
    def get_domains(self, page_size: int = 100, page: int = 1, sort_by: str = None, 
                 search_term: str = None, list_type: str = None) -> Dict[str, Any]:
        """
        Gets a list of domains in the user's account.
        
        Args:
            page_size: Number of domains to return per page (default: 100, max: 100)
            page: Page number to return (default: 1)
            sort_by: Column to sort by (DOMAINNAME, EXPIREDATE, CREATEDATE)
            search_term: Term to search for in the domain list
            list_type: Type of domains to include (ALL, EXPIRING, EXPIRED)
            
        Returns:
            Dictionary containing the API response with domain list
        """
        params = {
            'Page': str(page),
            'PageSize': str(min(page_size, 100))  # Ensure page size doesn't exceed 100
        }
        
        # Add optional parameters
        if sort_by:
            params['SortBy'] = sort_by
        
        if search_term:
            params['SearchTerm'] = search_term
            
        if list_type:
            params['ListType'] = list_type
        
        root = self._make_request('namecheap.domains.getList', params)
        
        domains_result = root.find('.//nc:CommandResponse/nc:DomainGetListResult', self.NAMESPACE)
        domains = []
        
        if domains_result is not None:
            for domain in domains_result.findall('.//nc:Domain', self.NAMESPACE):
                domain_data = {
                    'ID': domain.attrib.get('ID', ''),
                    'Name': domain.attrib.get('Name', ''),
                    'User': domain.attrib.get('User', ''),
                    'Created': domain.attrib.get('Created', ''),
                    'Expires': domain.attrib.get('Expires', ''),
                    'IsExpired': domain.attrib.get('IsExpired', '').lower() == 'true',
                    'IsLocked': domain.attrib.get('IsLocked', '').lower() == 'true',
                    'AutoRenew': domain.attrib.get('AutoRenew', '').lower() == 'true',
                    'WhoisGuard': domain.attrib.get('WhoisGuard', ''),
                    'IsPremium': domain.attrib.get('IsPremium', '').lower() == 'true',
                    'IsOurDNS': domain.attrib.get('IsOurDNS', '').lower() == 'true'
                }
                domains.append(domain_data)
            
            paging = domains_result.find('.//nc:Paging', self.NAMESPACE)
            paging_info = {}
            
            if paging is not None:
                paging_info = {
                    'TotalItems': int(paging.attrib.get('TotalItems', '0')),
                    'CurrentPage': int(paging.attrib.get('CurrentPage', '0')),
                    'PageSize': int(paging.attrib.get('PageSize', '0')),
                    'TotalPages': int(paging.attrib.get('TotalPages', '0'))
                }
            
            return {
                'Domains': domains,
                'Paging': paging_info
            }
        
        return {'Domains': [], 'Paging': {}}
    
    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """
        Gets detailed information about a specific domain.
        
        Args:
            domain_name: The domain name to get information for
            
        Returns:
            Dictionary containing detailed domain information
        """
        sld, tld = extract_domain_parts(domain_name)
        
        params = {
            'DomainName': domain_name
        }
        
        root = self._make_request('namecheap.domains.getInfo', params)
        
        domain_result = root.find('.//nc:CommandResponse/nc:DomainGetInfoResult', self.NAMESPACE)
        
        if domain_result is not None:
            def get_attr(el, attr, default=''):
                return el.attrib.get(attr, default) if el is not None else default
    
            domain_info = {
                'ID': get_attr(domain_result, 'ID'),
                'DomainName': get_attr(domain_result, 'DomainName'),
                'OwnerName': get_attr(domain_result, 'OwnerName'),
                'IsOwner': get_attr(domain_result, 'IsOwner', 'false').lower() == 'true',
                'IsPremium': get_attr(domain_result, 'IsPremium', 'false').lower() == 'true',
                'IsOurDNS': get_attr(domain_result, 'IsOurDNS', 'false').lower() == 'true',
                'IsPremiumDNS': get_attr(domain_result, 'IsPremiumDNS', 'false').lower() == 'true',
                'IsPremiumDNSRegistration': get_attr(domain_result, 'IsPremiumDNSRegistration', 'false').lower() == 'true',
                'IsExpired': get_attr(domain_result, 'IsExpired', 'false').lower() == 'true',
                'IsLocked': get_attr(domain_result, 'Status', '').lower() == 'locked',
                'AutoRenew': get_attr(domain_result, 'AutoRenew', 'false').lower() == 'true',
                'WhoisGuard': get_attr(domain_result, 'WhoisGuard', ''),
                'IsPremiumDomain': get_attr(domain_result, 'IsPremiumDomain', 'false').lower() == 'true',
                'CreatedDate': '',
                'ExpiredDate': '',
                'UpdatedDate': '',
            }

            domain_details = domain_result.find('.//nc:DomainDetails', self.NAMESPACE)
            if domain_details is not None:
                created_elem = domain_details.find('nc:CreatedDate', self.NAMESPACE)
                expired_elem = domain_details.find('nc:ExpiredDate', self.NAMESPACE)
                
                domain_info.update({
                    'CreatedDate': created_elem.text if created_elem is not None else '',
                    'ExpiredDate': expired_elem.text if expired_elem is not None else '',
                })
            
            nameservers = []
            for ns in domain_result.findall('.//nc:DNSDetails/nc:Nameserver', self.NAMESPACE):
                if ns.text:
                    nameservers.append(ns.text)
            
            dns_details = domain_result.find('.//nc:DNSDetails', self.NAMESPACE)
            if dns_details is not None:
                domain_info['DNSDetails'] = {
                    'ProviderType': get_attr(dns_details, 'ProviderType', ''),
                    'IsUsingOurDNS': get_attr(dns_details, 'IsUsingOurDNS', 'false').lower() == 'true',
                    'IsPremiumDNS': get_attr(dns_details, 'IsPremiumDNS', 'false').lower() == 'true',
                    'Nameservers': nameservers
                }
            else:
                domain_info['DNSDetails'] = {
                    'ProviderType': '',
                    'IsUsingOurDNS': False,
                    'IsPremiumDNS': False,
                    'Nameservers': nameservers
                }
            
            whois_guard = {'Enabled': False}
            wg_enabled = domain_result.attrib.get('WhoisGuard', '').lower()
            
            if wg_enabled == 'true' or wg_enabled == 'enabled':
                wg_info = domain_result.find('.//nc:Whoisguard', self.NAMESPACE)
                if wg_info is not None:
                    whois_guard = {
                        'Enabled': True,
                        'ID': get_attr(wg_info, 'ID'),
                        'ExpiredDate': get_attr(wg_info, 'ExpiredDate'),
                        'EmailDetails': {
                            'WhoisGuardEmail': get_attr(wg_info, 'WhoisGuardEmail'),
                            'ForwardedTo': get_attr(wg_info, 'ForwardedTo'),
                            'LastAutoEmailChangeDate': get_attr(wg_info, 'LastAutoEmailChangeDate'),
                            'AutoEmailChangeFrequencyDays': get_attr(wg_info, 'AutoEmailChangeFrequencyDays')
                        }
                    }
            
            domain_info['WhoisGuardInfo'] = whois_guard 
            
            return domain_info
        
        return {}
    
    def check_domains_availability(self, domains: Union[str, List[str]], suggestions: bool = False) -> Dict[str, Any]:
        """
        Checks the availability of one or multiple domain names.
        
        Args:
            domains: Single domain as a string or list of domains to check
            suggestions: Whether to include domain suggestions (default: False)
            
        Returns:
            Dictionary containing the availability results for each domain
            
        Example:
            # Check a single domain
            result = namecheap.check_domains_availability('example.com')
            
            # Check multiple domains
            result = namecheap.check_domains_availability(['example.com', 'test.com'])
            
            # Check with suggestions
            result = namecheap.check_domains_availability('example.com', suggestions=True)
        """
        # Convert single domain to list if needed
        if isinstance(domains, str):
            domains = [domains]
        
        # Join domains with comma for the API
        domains_str = ','.join(domains)
        
        params = {
            'DomainList': domains_str
        }
        
        # Add suggestions parameter if needed
        if suggestions:
            params['CheckType'] = 'REGISTER'
        
        root = self._make_request('namecheap.domains.check', params)
        
        # Parse the response
        command_response = root.find('.//nc:CommandResponse', self.NAMESPACE)
        
        if command_response is not None:
            domain_results = []
            
            # Parse each domain result
            for domain_result in command_response.findall('.//nc:DomainCheckResult', self.NAMESPACE):
                domain = domain_result.attrib.get('Domain', '')
                available = domain_result.attrib.get('Available', '').lower() == 'true'
                error_no = domain_result.attrib.get('ErrorNo', '0')
                description = domain_result.attrib.get('Description', '')
                is_premium = domain_result.attrib.get('IsPremiumName', '').lower() == 'true'
                premium_reg_price = domain_result.attrib.get('PremiumRegistrationPrice', '')
                premium_renew_price = domain_result.attrib.get('PremiumRenewalPrice', '')
                premium_restore_price = domain_result.attrib.get('PremiumRestorePrice', '')
                premium_transfer_price = domain_result.attrib.get('PremiumTransferPrice', '')
                icann_fee = domain_result.attrib.get('IcannFee', '')
                eap_fee = domain_result.attrib.get('EapFee', '')
                
                domain_info = {
                    'Domain': domain,
                    'Available': available,
                    'ErrorNo': error_no,
                    'Description': description,
                    'IsPremium': is_premium,
                    'Prices': {
                        'Registration': premium_reg_price if is_premium else None,
                        'Renewal': premium_renew_price if is_premium else None,
                        'Restore': premium_restore_price if is_premium else None,
                        'Transfer': premium_transfer_price if is_premium else None,
                        'IcannFee': icann_fee,
                        'EapFee': eap_fee
                    }
                }
                
                # Add premium pricing if available
                if is_premium and premium_reg_price:
                    domain_info['PremiumPricing'] = {
                        'Registration': premium_reg_price,
                        'Renewal': premium_renew_price,
                        'Restore': premium_restore_price,
                        'Transfer': premium_transfer_price
                    }
                
                domain_results.append(domain_info)
            
            # Parse suggestions if requested
            suggestions_list = []
            if suggestions:
                suggestions_el = command_response.find('.//nc:DomainCheckData/nc:DomainCheckResults', self.NAMESPACE)
                if suggestions_el is not None:
                    for sug in suggestions_el.findall('.//nc:DomainSuggestion', self.NAMESPACE):
                        sug_domain = sug.attrib.get('Name', '')
                        sug_available = sug.attrib.get('Available', '').lower() == 'true'
                        
                        suggestion = {
                            'Domain': sug_domain,
                            'Available': sug_available
                        }
                        
                        if sug_available:
                            suggestion['Price'] = sug.attrib.get('RegistrationPrice', '')
                            suggestion['PromoPrice'] = sug.attrib.get('PromoRegistrationPrice', '')
                            suggestion['IsPremium'] = sug.attrib.get('IsPremium', '').lower() == 'true'
                        
                        suggestions_list.append(suggestion)
                
                return {
                    'Results': domain_results,
                    'Suggestions': suggestions_list if suggestions_list else None
                }
            
            return {
                'Results': domain_results
            }
        
        return {'Results': []}