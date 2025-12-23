from auth.auth import OpsRampAuth
from auth.config import get_pod_config


def main():
    
    print("=" * 70)
    print("OpsRamp Template Cloning Tool")
    print("=" * 70)
    
    try:
        # Load POD configurations from .env file
        pod1_config = get_pod_config(1)
        # pod2_config = get_pod_config(2)
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        return
    
    # Step 1: Authenticate with POD1
    print("\n[1/2] Authenticating with POD1...")
    pod1_auth = OpsRampAuth(**pod1_config)
    
    try:
        pod1_token = pod1_auth.get_token()
        print(f"✓ POD1 authenticated successfully")
        print(f"  Token: {pod1_token['access_token'][:20]}...")
    except Exception as e:
        print(f"✗ POD1 authentication failed: {str(e)}")
        return
    
    # Step 2: Authenticate with POD2
    # print("\n[2/2] Authenticating with POD2...")
    # pod2_auth = OpsRampAuth(**pod2_config)
    
    # try:
    #     pod2_token = pod2_auth.get_token()
    #     print(f"✓ POD2 authenticated successfully")
    #     print(f"  Token: {pod2_token['access_token'][:20]}...")
    # except Exception as e:
    #     print(f"✗ POD2 authentication failed: {str(e)}")
    #     return
    
    # print("\n" + "=" * 70)
    # print("✓ Authentication complete for both PODs")
    # print("=" * 70)
    
    # TODO: Implement template cloning steps
    print("\n📋 Next steps to implement:")
    print("  1. Fetch template customizations from POD1")
    print("  2. Get global template ID")
    print("  3. Get cloned template ID")
    print("  4. Get customizations")
    print("  5. Clone DMP and templates to POD2")
    print("  6. Update cloned template customizations")


if __name__ == "__main__":
    main()
