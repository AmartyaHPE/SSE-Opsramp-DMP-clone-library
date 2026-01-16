import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import urllib3
from typing import Dict, List, Optional
from auth.auth import OpsRampAuth
from integration.integration import IntegrationInfo

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TemplateInfo:
    
    def __init__(self, template_id: str, name: str, app_name: str, native_type: str, 
                 version: str, scope: str = "GLOBAL", persona: str = ""):
        self.template_id = template_id
        self.name = name
        self.app_name = app_name
        self.native_type = native_type
        self.version = version
        self.scope = scope
        self.persona = persona
    
    def __repr__(self):
        return (f"TemplateInfo(id='{self.template_id[:8]}...', "
                f"app='{self.app_name}', native_type='{self.native_type}')")
    
    def to_dict(self) -> Dict:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'app_name': self.app_name,
            'native_type': self.native_type,
            'version': self.version,
            'scope': self.scope,
            'persona': self.persona
        }


class TemplateManager:
    
    def __init__(self, auth: OpsRampAuth, tenant_id: str):
        
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def get_global_template_ids(self, integration_info: IntegrationInfo) -> List[TemplateInfo]:
        
        templates = []
        
        print(f"    Fetching templates for {len(integration_info.native_types)} native type(s)...")
        
        for idx, native_type in enumerate(integration_info.native_types, 1):
            print(f"      [{idx}/{len(integration_info.native_types)}] {native_type}...", end=" ")
            
            template_info = self.get_template_id(
                app_name=integration_info.app_name,
                native_type=native_type,
                version=integration_info.version,
                persona=integration_info.persona
            )
            
            if template_info:
                print(f"✓ {len(template_info)} template(s)")
                templates.extend(template_info)
            else:
                print("⚠ No template found")
        
        return templates
    
    def get_template_id(self, app_name: str, native_type: str, version: str, persona: Optional[str] = None) -> List[TemplateInfo]:
        
        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates"
        
        query_parts = [
            "scope:GLOBAL",
            f"appName:{app_name}",
            f"nativeType:{native_type}",
            f"version:{version}"
        ]
        
        # Add persona filter only if it exists
        if persona and isinstance(persona, str) and persona.strip():
            query_parts.append(f"name:{persona}")
        
        query_string = "+".join(query_parts)
        
        params = {
            'queryString': query_string,
            'includeGatewaySDK': 'true'
        }
        
        headers = self.auth.get_auth_header()
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            
            data = response.json()
            templates = []
            
            for result in data.get('results', []):
                template = TemplateInfo(
                    template_id=result.get('id', ''),
                    name=result.get('name', ''),
                    app_name=result.get('appName', ''),
                    native_type=result.get('nativeType', ''),
                    version=str(result.get('version', '')),
                    scope=result.get('scope', 'GLOBAL'),
                    persona=persona or ''
                )
                templates.append(template)
            
            return templates
            
        except Exception as e:
            print(f"  ⚠ Error fetching template for {native_type}: {str(e)}")
            return []
    
    def print_template_summary(self, templates: List[TemplateInfo]) -> None:
        
        print("\n" + "=" * 80)
        print(f"Found {len(templates)} Global Template(s)")
        print("=" * 80)
        
        for idx, tmpl in enumerate(templates, 1):
            print(f"\n[{idx}] {tmpl.name}")
            print(f"    Template ID: {tmpl.template_id}")
            print(f"    App Name: {tmpl.app_name}")
            print(f"    Native Type: {tmpl.native_type}")
            print(f"    Version: {tmpl.version}")
            if tmpl.persona:
                print(f"    Persona: {tmpl.persona}")
            print(f"    Scope: {tmpl.scope}")
        
        print("\n" + "=" * 80)
