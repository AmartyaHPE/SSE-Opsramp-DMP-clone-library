"""
OpsRamp Template Cloning Tool
Automates cloning of DMPs and templates between PODs
"""
from auth.auth import OpsRampAuth
from auth.config import get_pod_config, get_tenant_ids
from integration.integration import IntegrationManager
from templates.templates import TemplateManager


def main():
    
    print("=" * 80)
    print("OpsRamp Template Cloning Tool")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: Load Configuration
    # ========================================================================
    try:
        print("\n[Step 1/5] Loading POD1 configuration...")
        pod1_config = get_pod_config(1)
        tenant_ids = get_tenant_ids(1)
        print("✓ POD1 configuration loaded")
        # pod2_config = get_pod_config(2)
    except ValueError as e:
        print(f"✗ Configuration Error: {str(e)}")
        return
    
    # ========================================================================
    # STEP 2: Authenticate with POD1
    # ========================================================================
    print("\n[Step 2/5] Authenticating with POD1...")
    pod1_auth = OpsRampAuth(**pod1_config)
    
    try:
        pod1_token = pod1_auth.get_token()
        print(f"✓ POD1 authenticated successfully")
        print(f"  Base URL: {pod1_config['base_url']}")
        print(f"  Token: {pod1_token['access_token'][:20]}...")
    except Exception as e:
        print(f"✗ POD1 authentication failed: {str(e)}")
        return
    
    # ========================================================================
    # STEP 3: Get Tenant/Client ID
    # ========================================================================
    print("\n[Step 3/5] Using Client ID from configuration...")
    tenant_id = tenant_ids.get('client_id', '')
    
    if not tenant_id:
        print("⚠ Client ID not found in .env file")
        tenant_id = input("  Enter POD1 Client ID (Tenant): ").strip()
        if not tenant_id:
            print("✗ Client ID is required to proceed")
            return
    
    print(f"✓ Using Client ID: {tenant_id}")
    
    # ========================================================================
    # STEP 4: Fetch Integration Details
    # ========================================================================
    print("\n[Step 4/5] Fetching integration details for 'alletra'...")
    
    try:
        # Initialize Integration Manager
        integration_mgr = IntegrationManager(pod1_auth, tenant_id)
        
        # Search for alletra integrations
        integrations = integration_mgr.get_integration_details(app_name="alletra")
        
        print(f"✓ Found {len(integrations)} alletra integration(s)")
        
        # Display summary
        integration_mgr.print_integration_summary(integrations)
            
    except Exception as e:
        print(f"✗ Failed to fetch integration details: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================================================
    # STEP 5: Fetch Global Template IDs
    # ========================================================================
    print("\n[Step 5/5] Fetching global template IDs...")
    print(f"  Apps to process: {len(integrations)}")
    
    try:
        # Initialize Template Manager
        template_mgr = TemplateManager(pod1_auth, tenant_id)
        
        # Collect all templates for all integrations
        all_templates = []
        
        # First loop: Iterate through each app/integration
        for app_idx, integration in enumerate(integrations, 1):
            print(f"\n  [{app_idx}/{len(integrations)}] Processing app: {integration.app_name}")
            print(f"    Version: {integration.version}")
            if integration.persona:
                print(f"    Persona: {integration.persona}")
            
            # Second loop (inside get_global_template_ids): Iterate through native types
            templates = template_mgr.get_global_template_ids(integration)
            
            print(f"    ✓ Total for {integration.app_name}: {len(templates)} template(s)")
            all_templates.extend(templates)
        
        print(f"\n✓ Grand Total: {len(all_templates)} template(s) across all apps")
        
        # Display template summary
        template_mgr.print_template_summary(all_templates)
        
        # Display summary by app
        print("\n" + "=" * 80)
        print("Summary: Templates by App")
        print("=" * 80)
        
        app_summary = {}
        for tmpl in all_templates:
            if tmpl.app_name not in app_summary:
                app_summary[tmpl.app_name] = []
            app_summary[tmpl.app_name].append(tmpl)
        
        # for app_name, templates in app_summary.items():
        #     print(f"\n{app_name}: {len(templates)} template(s)")
        #     for tmpl in templates:
        #         print(f"  • {tmpl.native_type}")
        #         print(f"    ID: {tmpl.template_id}")
            
    except Exception as e:
        print(f"✗ Failed to fetch template IDs: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("✓ Process Complete!")
    print("=" * 80)
    print(f"\nData collected (in memory):")
    print(f"  • {len(integrations)} integration(s)")
    print(f"  • {len(all_templates)} global template(s)")
    print("\n📋 Next steps to implement:")
    print("  1. Get cloned template ID")
    print("  2. Get customizations")
    print("  3. Clone DMP and templates to POD2")
    print("  4. Update cloned template customizations")
    print("=" * 80)


if __name__ == "__main__":
    main()
