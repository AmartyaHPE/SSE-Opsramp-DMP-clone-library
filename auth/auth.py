import requests
from typing import Dict, Optional
from datetime import datetime, timedelta


class OpsRampAuth:
    # Handles authentication with OpsRamp API using OAuth2 client credentials flow.
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        # Initialize OpsRamp authentication.

        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.scope: Optional[str] = None
    
    def get_token(self) -> Dict[str, str]:
      
        # Checking valid token
        if self.access_token and self.expires_at:
            if datetime.now() < self.expires_at:
                return {
                    'access_token': self.access_token,
                    'token_type': self.token_type,
                    'scope': self.scope,
                    'expires_at': self.expires_at.isoformat()
                }
        
        # Gen. new token
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
        
        # make POST request to get token
        response = requests.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Store token information
        self.access_token = token_data['access_token']
        self.token_type = token_data['token_type']
        self.scope = token_data.get('scope', '')
        expires_in = token_data.get('expires_in', 7199)
        
        # Calculate expiration time (60 second buffer)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'scope': self.scope,
            'expires_in': expires_in,
            'expires_at': self.expires_at.isoformat()
        }
    
    def get_auth_header(self) -> Dict[str, str]:

        # returns "Authorization" header
        token_info = self.get_token()
        return {
            'Authorization': f"Bearer {token_info['access_token']}"
        }
    
    def refresh_token(self) -> Dict[str, str]:
        # Force refresh the access token.
        
        self.access_token = None
        self.expires_at = None
        return self.get_token()