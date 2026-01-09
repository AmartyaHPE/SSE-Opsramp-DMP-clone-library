# Fetches cloned template IDs using global template IDs as parent references.

import sys
from pathlib import Path

# parent directory path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import urllib3
from typing import Dict, List, Optional
from auth.auth import OpsRampAuth
from templates.templates import TemplateInfo

# SSL warnings disabled (temporary)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ClonedTemplateInfo:
    """Data class to store cloned template information"""
    
    def __init__(self, template_id: str, name: str, scope: str, parent_id: str,
                 app_name: str = "", native_type: str = "", version: str = ""):
        self.template_id = template_id
        self.name = name
        self.scope = scope
        self.parent_id = parent_id
        self.app_name = app_name
        self.native_type = native_type
        self.version = version
    
    def __repr__(self):
        return (f"ClonedTemplateInfo(id='{self.template_id[:8]}...', "
                f"name='{self.name}', scope='{self.scope}')")
    
    def to_dict(self) -> Dict:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'scope': self.scope,
            'parent_id': self.parent_id,
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
        """
        Initialize ClonedTemplateManager.
        
        Args:
            auth: OpsRampAuth instance for API authentication
            tenant_id: Tenant/Client ID for API requests
        """
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def get_cloned_templates(self, global_template_id: str, 
                            app_name: str = "", native_type: str = "", 
                            version: str = "") -> List[ClonedTemplateInfo]:
        """
        Fetch cloned templates for a specific global template parent.
        
        Args:
            global_template_id: The parent global template ID
            app_name: App name for metadata (optional)
            native_type: Native type for metadata (optional)
            version: Version for metadata (optional)
            
        Returns:
            List of ClonedTemplateInfo objects
        """
        # Build query string: scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{id}
        query_string = f"scope:GLOBAL,SERVICE PROVIDER,CLIENT,PARTNER+parentId:{global_template_id}"
        
        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates"
        params = {'queryString': query_string}
        headers = self.auth.get_auth_header()
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                cloned_templates = []
                for item in results:
                    cloned = ClonedTemplateInfo(
                        template_id=item.get('id', ''),
                        name=item.get('name', ''),
                        scope=item.get('scope', ''),
                        parent_id=global_template_id,
                        app_name=app_name,
                        native_type=native_type,
                        version=version
                    )
                    cloned_templates.append(cloned)
                
                return cloned_templates
            else:
                # Silently ignore errors (some global templates may have no clones)
                return []
                
        except Exception as e:
            # Silently ignore errors
            return []
    
    def get_all_cloned_templates(self, global_templates: List[TemplateInfo]) -> Dict[str, List[ClonedTemplateInfo]]:
        """
        Fetch all cloned templates for a list of global templates.
        
        Args:
            global_templates: List of global TemplateInfo objects
            
        Returns:
            Dictionary mapping global_template_id -> list of ClonedTemplateInfo
        """
        print(f"\n  Processing {len(global_templates)} global template(s)...")
        
        cloned_dict = {}
        
        for idx, global_tmpl in enumerate(global_templates, 1):
            clones = self.get_cloned_templates(
                global_template_id=global_tmpl.template_id,
                app_name=global_tmpl.app_name,
                native_type=global_tmpl.native_type,
                version=global_tmpl.version
            )
            
            cloned_dict[global_tmpl.template_id] = clones
            
            # Progress indicator
            if len(clones) > 0:
                print(f"  [{idx}/{len(global_templates)}] {global_tmpl.native_type}: ✓ {len(clones)} clone(s)")
            else:
                print(f"  [{idx}/{len(global_templates)}] {global_tmpl.native_type}: - No clones")
        
        return cloned_dict
    
    def print_cloned_templates_summary(self, cloned_templates_dict: Dict[str, List[ClonedTemplateInfo]], 
                                       global_templates: List[TemplateInfo]) -> None:
        """
        Print summary of cloned templates grouped by their parent global template.
        
        Args:
            cloned_templates_dict: Dictionary mapping global_template_id -> list of cloned templates
            global_templates: List of global templates to display parent info
        """
        print("\n" + "=" * 80)
        print("CLONED TEMPLATES SUMMARY")
        print("=" * 80)
        
        # Create lookup dict for global templates
        global_lookup = {t.template_id: t for t in global_templates}
        
        # Count total clones
        total_clones = sum(len(clones) for clones in cloned_templates_dict.values())
        print(f"\nTotal Cloned Templates Found: {total_clones}")
        
        if total_clones == 0:
            print("\nNo cloned templates found.")
            print("=" * 80)
            return
        
        # Print grouped by parent
        print("\n" + "-" * 80)
        for global_id, clones in cloned_templates_dict.items():
            if len(clones) == 0:
                continue
                
            # Get parent info
            parent = global_lookup.get(global_id)
            if parent:
                print(f"\n[PARENT GLOBAL TEMPLATE]")
                print(f"  Name: {parent.name}")
                print(f"  ID: {parent.template_id}")
                print(f"  App: {parent.app_name} | Type: {parent.native_type} | Version: {parent.version}")
                if parent.persona:
                    print(f"  Persona: {parent.persona}")
            else:
                print(f"\n[PARENT GLOBAL TEMPLATE ID: {global_id}]")
            
            print(f"\n  Cloned Templates ({len(clones)}):")
            for idx, clone in enumerate(clones, 1):
                print(f"\n  [{idx}] {clone.name}")
                print(f"      Template ID: {clone.template_id}")
                print(f"      Scope: {clone.scope}")
        
        print("\n" + "=" * 80)
