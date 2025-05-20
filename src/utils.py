from typing import Tuple

def extract_domain_parts(domain_name: str) -> Tuple[str, str]:
    """Extract SLD and TLD from domain_name"""
    domain_parts = domain_name.split('.')
    if len(domain_parts) >= 2:
        sld = domain_parts[0]
        tld = '.'.join(domain_parts[1:])
        return sld, tld
    else:
        raise ValueError(f"Invalid domain name: {domain_name}")