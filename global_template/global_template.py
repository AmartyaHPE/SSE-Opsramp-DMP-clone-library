import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import urllib3
from typing import Dict, Optional
from urllib.parse import quote
from auth.auth import OpsRampAuth

# Disable SSL warnings (temporary for development)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GlobalTemplateInfo:
    # data class for global template
    
    def __init__(self, template_id: str, name: str, description: str = "",
                 app_name: str = "", native_type: str = "", version: str = "",
                 scope: str = "GLOBAL", raw_response: Dict = None):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.app_name = app_name
        self.native_type = native_type
        self.version = version
        self.scope = scope
        self.raw_response = raw_response or {}
    
    def __repr__(self):
        return (f"GlobalTemplateInfo(id='{self.template_id[:8]}...', "
                f"name='{self.name[:40]}...')")
    
    def to_dict(self) -> Dict:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'app_name': self.app_name,
            'native_type': self.native_type,
            'version': self.version,
            'scope': self.scope
        }


class GlobalTemplateManager:
    
    def __init__(self, auth: OpsRampAuth, tenant_id: str):
        
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def get_global_template_by_name(self, template_name: str) -> Optional[GlobalTemplateInfo]:
        # API: GET https://{base_url}/api/v2/tenants/{tenantId}/templates?queryString=scope:GLOBAL+name:{template_name}&includeGatewaySDK=true

        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates"
        
        # Build query string - don't pre-encode, let requests handle it
        # The + is used as a separator in OpsRamp API
        query_string = f"scope:GLOBAL+name:{template_name}"
        
        params = {
            'queryString': query_string,
            'includeGatewaySDK': 'true'
        }
        
        headers = self.auth.get_auth_header()
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    print(f"  ⚠ No global template found with name: {template_name}")
                    return None
                
                # Get the first matching result
                item = results[0]
                
                template_info = GlobalTemplateInfo(
                    template_id=item.get('id', ''),
                    name=item.get('name', ''),
                    description=item.get('description', ''),
                    app_name=item.get('appName', ''),
                    native_type=item.get('nativeType', ''),
                    version=str(item.get('version', '')),
                    scope=item.get('scope', 'GLOBAL'),
                    raw_response=item
                )
                
                return template_info
            else:
                print(f"  ✗ API Error [{response.status_code}]: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {str(e)}")
            return None
    
    def get_global_template_id(self, template_name: str) -> Optional[str]:
       
        template_info = self.get_global_template_by_name(template_name)
        return template_info.template_id if template_info else None


# Standalone function for simple usage
def get_global_template_id(auth: OpsRampAuth, tenant_id: str, template_name: str) -> Optional[str]:
    manager = GlobalTemplateManager(auth, tenant_id)
    return manager.get_global_template_id(template_name)
