"""
OpsRamp Template Cloning Tool
Automates cloning of DMPs and templates between PODs
"""
from auth.auth import OpsRampAuth
from auth.config import get_pod_config, get_tenant_ids
from integration.integration import IntegrationManager


def main():
    
    print("=" * 80)
    print("OpsRamp Template Cloning Tool")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: Load Configuration
    # ========================================================================
    try:
        print("\n[Step 1/4] Loading POD1 configuration...")
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
    print("\n[Step 2/4] Authenticating with POD1...")
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
    print("\n[Step 3/4] Using Client ID from configuration...")
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
    print("\n[Step 4/4] Fetching integration details for 'alletra'...")
    
    try:
        # Initialize Integration Manager
        integration_mgr = IntegrationManager(pod1_auth, tenant_id)
        
        # Search for alletra integrations
        integrations = integration_mgr.get_integration_details(app_name="alletra")
        
        print(f"✓ Found {len(integrations)} alletra integration(s)")
        
        # Display summary
        integration_mgr.print_integration_summary(integrations)
        
        # Display extracted data (stored in memory)
        print("\n" + "=" * 80)
        print("Extracted Integration Data:")
        print("=" * 80)
        for idx, info in enumerate(integrations, 1):
            print(f"\n[{idx}] {info.app_name}")
            print(f"    Version: {info.version}")
            print(f"    Persona: {info.persona if info.persona else '(empty)'}")
            print(f"    Native Types: {len(info.native_types)} types")
            
    except Exception as e:
        print(f"✗ Failed to fetch integration details: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("✓ Process Complete!")
    print("=" * 80)
    print("\n📋 Next steps to implement:")
    print("  1. Get global template ID")
    print("  2. Get cloned template ID")
    print("  3. Get customizations")
    print("  4. Clone DMP and templates to POD2")
    print("  5. Update cloned template customizations")
    print("=" * 80)


if __name__ == "__main__":
    main()
