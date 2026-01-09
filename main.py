"""
OpsRamp Template Cloning Tool
Automates cloning of DMPs and templates between PODs
"""
from auth.auth import OpsRampAuth
from auth.config import get_pod_config, get_tenant_ids
from integration.integration import IntegrationManager
from templates.templates import TemplateManager
from cloned_templates.cloned_templates import ClonedTemplateManager


def main():
    
    print("=" * 80)
    print("OpsRamp Template Cloning Tool")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: Load Configuration
    # ========================================================================
    try:
        print("\n[Step 1/6] Loading POD1 configuration...")
        pod1_config = get_pod_config(1)
        tenant_ids = get_tenant_ids(1)
        print("✓ Configuration loaded")
    except ValueError as e:
        print(f"✗ Configuration Error: {str(e)}")
        return
    
    # ========================================================================
    # STEP 2: Authenticate with POD1
    # ========================================================================
    print("\n[Step 2/6] Authenticating with POD1...")
    pod1_auth = OpsRampAuth(**pod1_config)
    
    try:
        pod1_token = pod1_auth.get_token()
        print("✓ Authenticated")
    except Exception as e:
        print(f"✗ Authentication failed: {str(e)}")
        return
    
    # ========================================================================
    # STEP 3: Get Tenant/Client ID
    # ========================================================================
    print("\n[Step 3/6] Getting Client ID...")
    tenant_id = tenant_ids.get('client_id', '')
    
    if not tenant_id:
        print("✗ Client ID not found in .env file")
        return
    
    print("✓ Client ID loaded")
    
    # ========================================================================
    # STEP 4: Fetch Integration Details
    # ========================================================================
    print("\n[Step 4/6] Fetching integration details...")
    
    try:
        integration_mgr = IntegrationManager(pod1_auth, tenant_id)
        integrations = integration_mgr.get_integration_details(app_name="alletra")
        print(f"✓ Found {len(integrations)} integration(s)")
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return
    
    # ========================================================================
    # STEP 5: Fetch Global Template IDs
    # ========================================================================
    print("\n[Step 5/6] Fetching global template IDs...")
    
    try:
        template_mgr = TemplateManager(pod1_auth, tenant_id)
        all_templates = []
        
        for integration in integrations:
            templates = template_mgr.get_global_template_ids(integration)
            all_templates.extend(templates)
        
        print(f"✓ Found {len(all_templates)} global template(s)")
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return
    
    # ========================================================================
    # STEP 6: Fetch Cloned Template IDs
    # ========================================================================
    print("\n[Step 6/6] Fetching cloned template IDs...")
    
    try:
        cloned_mgr = ClonedTemplateManager(pod1_auth, tenant_id)
        cloned_dict = cloned_mgr.get_all_cloned_templates(all_templates)
        
        total_clones = sum(len(clones) for clones in cloned_dict.values())
        print(f"✓ Found {total_clones} cloned template(s)")
        
        # Display cloned templates with parent info
        print("\n" + "=" * 80)
        print("CLONED TEMPLATES")
        print("=" * 80)
        
        if total_clones == 0:
            print("\nNo cloned templates found.")
        else:
            for global_id, clones in cloned_dict.items():
                if len(clones) > 0:
                    print(f"\nGlobal Template ID: {global_id}")
                    for clone in clones:
                        print(f"  → Cloned Template ID: {clone.template_id}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return


if __name__ == "__main__":
    main()
