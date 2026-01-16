import requests
from typing import Dict, Optional
from datetime import datetime, timedelta


class OpsRampAuth:
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):

        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.scope: Optional[str] = None
    
    def get_token(self) -> Dict[str, str]:
      
        if self.access_token and self.expires_at:
            if datetime.now() < self.expires_at:
                return {
                    'access_token': self.access_token,
                    'token_type': self.token_type,
                    'scope': self.scope,
                    'expires_at': self.expires_at.isoformat()
                }
        
        url = f"{self.base_url}/tenancy/auth/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        
        token_data = response.json()
        
        self.access_token = token_data['access_token']
        self.token_type = token_data['token_type']
        self.scope = token_data.get('scope', '')
        expires_in = token_data.get('expires_in', 7199)
        
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'scope': self.scope,
            'expires_in': expires_in,
            'expires_at': self.expires_at.isoformat()
        }
    
    def get_auth_header(self) -> Dict[str, str]:

        token_info = self.get_token()
        return {
            'Authorization': f"Bearer {token_info['access_token']}"
        }
    
    def refresh_token(self) -> Dict[str, str]:
        
        self.access_token = None
        self.expires_at = None
        return self.get_token()