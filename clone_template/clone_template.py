"""
Clone Template Module
Clones a template to POD-2 using the customization payload from POD-1.
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


class CloneTemplateManager:
    """
    Manages cloning templates to a target POD using OpsRamp API.
    Takes a customization payload from source POD and clones it to target POD.
    """
    
    def __init__(self, auth: OpsRampAuth, tenant_id: str):
        """
        Initialize CloneTemplateManager.
        
        Args:
            auth: OpsRampAuth instance for API authentication
            tenant_id: Tenant ID for API requests (target POD)
        """
        self.auth = auth
        self.tenant_id = tenant_id
        self.base_url = auth.base_url
    
    def prepare_clone_payload(self, source_customizations: Dict, 
                               target_global_template_id: str,
                               new_template_name: Optional[str] = None) -> Dict:
        """
        Prepare the clone request payload from source customizations.
        
        Steps:
        1. Remove the 'id' field from the source payload
        2. Add 'clonedTemplateId' field with target global template ID
        3. Optionally update the 'name' field
        
        Args:
            source_customizations: The customization payload from POD-1
            target_global_template_id: Global template ID from POD-2
            new_template_name: Optional new name for the cloned template
            
        Returns:
            Prepared payload for clone API request
        """
        # Create a copy to avoid modifying the original
        payload = source_customizations.copy()
        
        # Remove the 'id' field if exists
        if 'id' in payload:
            del payload['id']
        
        # Add clonedTemplateId with target global template ID
        payload['clonedTemplateId'] = target_global_template_id
        
        # Update name if provided
        if new_template_name:
            payload['name'] = new_template_name
        
        return payload
    
    def clone_template(self, source_customizations: Dict,
                       target_global_template_id: str,
                       new_template_name: Optional[str] = None) -> Optional[Dict]:
        """
        Clone a template using the customization payload.
        
        API: POST https://{base_url}/monitoring/api/v3/tenants/{tenantId}/templates/clone
        
        Args:
            source_customizations: The customization payload from POD-1
            target_global_template_id: Global template ID from POD-2
            new_template_name: Optional new name for the cloned template
            
        Returns:
            Clone response containing the new template ID, None if failed
        """
        url = f"{self.base_url}/monitoring/api/v3/tenants/{self.tenant_id}/templates/clone"
        
        # Prepare the payload
        payload = self.prepare_clone_payload(
            source_customizations, 
            target_global_template_id,
            new_template_name
        )
        
        headers = self.auth.get_auth_header()
        headers['Content-Type'] = 'application/json'
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False)
            
            if response.status_code in [200, 201]:
                clone_response = response.json()
                print(f"  ✓ Template cloned successfully!")
                
                # Extract and display the new template ID
                new_template_id = clone_response.get('id', 'N/A')
                print(f"    New Template ID: {new_template_id}")
                
                return clone_response
            else:
                print(f"  ✗ Clone API Error [{response.status_code}]: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {str(e)}")
            return None
    
    def get_cloned_template_id(self, clone_response: Dict) -> Optional[str]:
        """
        Extract the template ID from clone response.
        
        Args:
            clone_response: Response from clone API
            
        Returns:
            Template ID string, None if not found
        """
        return clone_response.get('id') if clone_response else None
    
    def save_clone_response(self, clone_response: Dict, filename: str) -> bool:
        """
        Save clone response to a JSON file.
        
        Args:
            clone_response: Response from clone API
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            output_dir = Path(__file__).parent.parent / 'output'
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clone_response, f, indent=4)
            
            print(f"  ✓ Saved clone response to: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to save response: {str(e)}")
            return False


# Standalone function for simple usage
def clone_template(auth: OpsRampAuth, tenant_id: str, 
                   source_customizations: Dict,
                   target_global_template_id: str,
                   new_template_name: Optional[str] = None) -> Optional[Dict]:
    """
    Standalone function to clone a template.
    
    Args:
        auth: OpsRampAuth instance
        tenant_id: Target tenant ID
        source_customizations: Customization payload from source POD
        target_global_template_id: Global template ID in target POD
        new_template_name: Optional new name for cloned template
        
    Returns:
        Clone response dictionary, None if failed
    """
    manager = CloneTemplateManager(auth, tenant_id)
    return manager.clone_template(
        source_customizations, 
        target_global_template_id,
        new_template_name
    )
