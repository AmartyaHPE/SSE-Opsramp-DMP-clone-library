"""
Test script for Cloned Template Manager component.
Tests fetching cloned templates using global template IDs as parent references.
"""
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from auth.auth import OpsRampAuth
from auth.config import get_pod_config, get_tenant_ids
from integration.integration import IntegrationManager
from templates.templates import TemplateManager
from cloned_templates.cloned_templates import ClonedTemplateManager


def main():
    print("=" * 80)
    print("Cloned Template Manager Test")
    print("=" * 80)
    
    # Load configuration
    print("\n[1/5] Loading POD1 configuration...")
    try:
        pod1_config = get_pod_config(1)
        tenant_ids = get_tenant_ids(1)
        print("✓ Configuration loaded")
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Authenticate
    print("\n[2/5] Authenticating with POD1...")
    pod1_auth = OpsRampAuth(**pod1_config)
    
    try:
        token = pod1_auth.get_token()
        print(f"✓ Authenticated successfully")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    tenant_id = tenant_ids.get('client_id', '')
    if not tenant_id:
        print("✗ Client ID not found")
        return
    
    # Fetch integrations
    print("\n[3/5] Fetching alletra integrations...")
    try:
        integration_mgr = IntegrationManager(pod1_auth, tenant_id)
        integrations = integration_mgr.get_integration_details(app_name="alletra")
        print(f"✓ Found {len(integrations)} integration(s)")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    # Fetch global templates
    print("\n[4/5] Fetching global template IDs...")
    try:
        template_mgr = TemplateManager(pod1_auth, tenant_id)
        
        all_templates = []
        for integration in integrations:
            templates = template_mgr.get_global_template_ids(integration)
            all_templates.extend(templates)
        
        print(f"✓ Found {len(all_templates)} global template(s)")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    # Fetch cloned templates
    print("\n[5/5] Fetching cloned templates...")
    try:
        cloned_mgr = ClonedTemplateManager(pod1_auth, tenant_id)
        cloned_dict = cloned_mgr.get_all_cloned_templates(all_templates)
        
        total_clones = sum(len(clones) for clones in cloned_dict.values())
        print(f"\n✓ Found {total_clones} cloned template(s)")
        
        # Display summary
        cloned_mgr.print_cloned_templates_summary(cloned_dict, all_templates)
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✓ Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
