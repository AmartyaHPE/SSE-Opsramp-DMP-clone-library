"""
Template Customizations Module
Fetches the full customization payload (JSON body) of a cloned template.
This payload is needed for cloning to POD-2.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import requests
import urllib3
from typing import Dict, Optional
from auth.auth import OpsRampAuth

# Disable SSL warnings (temporary for development)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TemplateCustomizationsManager:
    """
    Manages fetching template customizations from OpsRamp API.
    Retrieves the full JSON body of a template which is needed for cloning.
    """
    
    def __init__(self, auth: OpsRampAuth, tenant_id: str):
        """
        Initialize TemplateCustomizationsManager.
        
        Args:
            auth: OpsRampAuth instance for API authentication
            tenant_id: Tenant ID for API requests
        """
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def get_template_customizations(self, cloned_template_id: str) -> Optional[Dict]:
        """
        Fetch the full customization payload of a cloned template.
        
        API: GET https://{base_url}/api/v2/tenants/{tenantId}/templates/{templateId}
        
        Args:
            cloned_template_id: The cloned template ID
            
        Returns:
            Full template JSON payload as dictionary, None if failed
        """
        url = f"{self.base_url}/api/v2/tenants/{self.tenant_id}/templates/{cloned_template_id}"
        
        headers = self.auth.get_auth_header()
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ✗ API Error [{response.status_code}]: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {str(e)}")
            return None
    
    def save_customizations_to_file(self, customizations: Dict, filename: str) -> bool:
        """
        Save customizations payload to a JSON file.
        
        Args:
            customizations: Template customizations dictionary
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            output_dir = Path(__file__).parent.parent / 'output'
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(customizations, f, indent=4)
            
            print(f"  ✓ Saved customizations to: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to save customizations: {str(e)}")
            return False


# Standalone function for simple usage
def get_template_customizations(auth: OpsRampAuth, tenant_id: str, 
                                cloned_template_id: str) -> Optional[Dict]:
    """
    Standalone function to fetch template customizations.
    
    Args:
        auth: OpsRampAuth instance
        tenant_id: Tenant ID
        cloned_template_id: Cloned template ID
        
    Returns:
        Template customizations as dictionary, None if failed
    """
    manager = TemplateCustomizationsManager(auth, tenant_id)
    return manager.get_template_customizations(cloned_template_id)
