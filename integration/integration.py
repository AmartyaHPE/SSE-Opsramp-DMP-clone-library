# Extracts app name, native types, versions, and persona information.

import sys
from pathlib import Path

# parent directory path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import urllib3
from typing import Dict, List, Optional
from auth.auth import OpsRampAuth

# SSL warnings disabled (temporary)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IntegrationInfo:
    # custom data class for integration information
    
    def __init__(self, app_name: str, native_types: List[str], version: str, persona: str = ""):
        self.app_name = app_name
        self.native_types = native_types
        self.version = version
        self.persona = persona
    
    def __repr__(self):
        return (f"IntegrationInfo(app_name='{self.app_name}', "
                f"native_types={len(self.native_types)} items, "
                f"version='{self.version}', persona='{self.persona}')")
    
    def to_dict(self) -> Dict:
        return {
            'app_name': self.app_name,
            'native_types': self.native_types,
            'version': self.version,
            'persona': self.persona
        }


class IntegrationManager:
    
    def __init__(self, auth: OpsRampAuth, client_id: str):
        
        self.auth = auth
        self.client_id = client_id
        self.base_url = auth.base_url
    
    def search_integrations(self, category: str = "SDK", app_name: Optional[str] = None) -> Dict:
        
        # Args:
        #     category: Integration category (default: "SDK")
        #     app_name: Optional app name to filter (e.g., "alletra")
        
        url = f"{self.base_url}/api/v2/tenants/{self.client_id}/integrations/available/search"
        
        # Build query string
        if app_name:
            query_string = f"category:{category}+name:{app_name}"
        else:
            query_string = f"category:{category}"
        
        params = {'queryString': query_string}
        headers = self.auth.get_auth_header()
        
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        
        return response.json()
    
    def extract_integration_info(self, api_response: Dict) -> List[IntegrationInfo]:
        
        integrations = []
        
        for result in api_response.get('results', []):
            app_name = result.get('name', '')
            
            native_types = [nt['label'] for nt in result.get('nativeType', [])]
            
            versions = result.get('versions', [])
            version = self._get_latest_major_version(versions)
            
            metadata = result.get('metaData', {})
            persona = metadata.get('resourceHierarchy', '')
            
            info = IntegrationInfo(
                app_name=app_name,
                native_types=native_types,
                version=version,
                persona=persona
            )
            integrations.append(info)
        
        return integrations
    
    def _get_latest_major_version(self, versions: List[Dict]) -> str:

        if not versions:
            return "unknown"
        
        published = [v for v in versions if v.get('state') == 'Published']
        
        if not published:
            return "unknown"
        
        latest = published[-1]['tag']
        
        major_version = latest.split('.')[0]
        
        return major_version
    
    def get_integration_details(self, app_name: Optional[str] = None) -> List[IntegrationInfo]:
        # Returns List of IntegrationInfo objects

        response = self.search_integrations(category="SDK", app_name=app_name)
        return self.extract_integration_info(response)
    
    def print_integration_summary(self, integrations: List[IntegrationInfo]) -> None:
        print("\n" + "=" * 80)
        print(f"Found {len(integrations)} integration(s)")
        print("=" * 80)
        
        for idx, info in enumerate(integrations, 1):
            print(f"\n[{idx}] App: {info.app_name}")
            print(f"    Version: {info.version}")
            if info.persona:
                print(f"    Persona: {info.persona}")
            print(f"    Native Types ({len(info.native_types)}):")
            for nt in info.native_types:
                print(f"      • {nt}")
        
        print("\n" + "=" * 80)
