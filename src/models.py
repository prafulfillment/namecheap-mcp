from pydantic import BaseModel, Field
from typing import Dict

class EmailForward(BaseModel):
    """Represents an email forwarding record for Namecheap DNS."""
    mailbox: str = Field(description="The part before @ in your domain email")
    forward_to: str = Field(description="The destination email address")
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API."""
        return {
            'MailBox': self.mailbox,
            'ForwardTo': self.forward_to
        }


class HostRecord(BaseModel):
    """Represents a DNS host record for Namecheap DNS."""
    hostname: str = Field(description="The hostname/subdomain (@ for root domain)")
    record_type: str = Field(description="A, AAAA, CNAME, MX, TXT, etc.")
    address: str = Field(description="IP address, domain name, or text content depending on record type")
    mx_pref: str = Field(default="10", description="MX preference, only used for MX records")
    ttl: str = Field(default="1800", description="Time to live in seconds")
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API."""
        result = {
            'HostName': self.hostname,
            'RecordType': self.record_type,
            'Address': self.address,
            'TTL': self.ttl
        }
        
        if self.record_type == "MX":
            result['MXPref'] = self.mx_pref
            
        return result