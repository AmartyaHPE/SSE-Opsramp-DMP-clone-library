import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import urllib3
from typing import Dict, Optional, List
from auth.auth import OpsRampAuth

# Disable SSL warnings (temporary for development)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ClonedTemplateInfo:
    
    def __init__(self, template_id: str, name: str, description: str = "",
                 parent_id: str = "", scope: str = "", app_name: str = "",
                 native_type: str = "", version: str = "", raw_response: Dict = None):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.scope = scope
        self.app_name = app_name
        self.native_type = native_type
        self.version = version
        self.raw_response = raw_response or {}
    
    def __repr__(self):
        return (f"ClonedTemplateInfo(id='{self.template_id[:8]}...', "
                f"name='{self.name[:40]}...', scope='{self.scope}')")
    
    def to_dict(self) -> Dict:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'scope': self.scope,
            'app_name': self.app_name,
            'native_type': self.native_type,
            'version': self.version
        }


class ClonedTemplateManager:
    """
    Manages fetching cloned templates from OpsRamp API.
    Cloned templates are identified using their parent global template IDs.
    """
    
    def __init__(self, auth: OpsRampAuth, tenant_id: str):
      
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def get_cloned_template_by_parent_id(self, global_template_id: str) -> Optional[ClonedTemplateInfo]:
        
        # API: GET https://{base_url}/api/v2/tenants/{tenantId}/templates
        #      ?queryString=scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{globalTemplateId}
        #      &includeGatewaySDK=true
        
        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates"
        
        # Build query string: scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{id}
        query_string = f"scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{global_template_id}"
        
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
                    print(f"  ⚠ No cloned template found for parent ID: {global_template_id}")
                    return None
                
                # Get the first matching result
                item = results[0]
                
                cloned_info = ClonedTemplateInfo(
                    template_id=item.get('id', ''),
                    name=item.get('name', ''),
                    description=item.get('description', ''),
                    parent_id=item.get('parentUUID', global_template_id),
                    scope=item.get('scope', ''),
                    app_name=item.get('appName', ''),
                    native_type=item.get('nativeType', ''),
                    version=str(item.get('version', '')),
                    raw_response=item
                )
                
                return cloned_info
            else:
                print(f"  ✗ API Error [{response.status_code}]: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {str(e)}")
            return None
    
    def get_all_cloned_templates_by_parent_id(self, global_template_id: str) -> List[ClonedTemplateInfo]:
        
        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates"
        
        query_string = f"scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{global_template_id}"
        
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
                
                cloned_templates = []
                for item in results:
                    cloned_info = ClonedTemplateInfo(
                        template_id=item.get('id', ''),
                        name=item.get('name', ''),
                        description=item.get('description', ''),
                        parent_id=item.get('parentUUID', global_template_id),
                        scope=item.get('scope', ''),
                        app_name=item.get('appName', ''),
                        native_type=item.get('nativeType', ''),
                        version=str(item.get('version', '')),
                        raw_response=item
                    )
                    cloned_templates.append(cloned_info)
                
                return cloned_templates
            else:
                print(f"  ✗ API Error [{response.status_code}]: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {str(e)}")
            return []
    
    def get_cloned_template_id(self, global_template_id: str) -> Optional[str]:
        
        cloned_info = self.get_cloned_template_by_parent_id(global_template_id)
        return cloned_info.template_id if cloned_info else None


# Standalone function for simple usage
def get_cloned_template_id(auth: OpsRampAuth, tenant_id: str, global_template_id: str) -> Optional[str]:
    
    manager = ClonedTemplateManager(auth, tenant_id)
    return manager.get_cloned_template_id(global_template_id)
