"""
Test script for OpsRamp authentication.
Loads credentials from .env file.
"""
from auth import OpsRampAuth
from config import get_default_config
import json


def test_authentication():
    """Test basic authentication flow"""
    print("=" * 60)
    print("Testing OpsRamp Authentication")
    print("=" * 60)
    
    # Load configuration from .env file
    try:
        config = get_default_config()
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        print("\nMake sure your .env file exists and has the required variables:")
        print("  OPSRAMP_BASE_URL")
        print("  OPSRAMP_CLIENT_ID")
        print("  OPSRAMP_CLIENT_SECRET")
        return False
    
    # Initialize auth
    print("\n1. Initializing authentication...")
    auth = OpsRampAuth(**config)
    
    try:
        # Get token
        print("\n2. Requesting access token...")
        token_info = auth.get_token()
        
        print("\n✓ Token retrieved successfully!")
        print(f"   Token Type: {token_info['token_type']}")
        print(f"   Access Token: {token_info['access_token'][:20]}...{token_info['access_token'][-20:]}")
        print(f"   Scope: {token_info['scope']}")
        print(f"   Expires In: {token_info['expires_in']} seconds")
        print(f"   Expires At: {token_info['expires_at']}")
        
        # Get auth header (this should reuse the cached token)
        print("\n3. Getting authorization header...")
        auth_header = auth.get_auth_header()
        print(f"   Authorization: {auth_header['Authorization'][:30]}...")
        
        # Test token reuse (should use cached token)
        print("\n4. Testing token reuse (should use cached token)...")
        token_info2 = auth.get_token()
        if token_info2['access_token'] == token_info['access_token']:
            print("   ✓ Token correctly reused from cache")
        
        # Pretty print full token response
        print("\n5. Full token information:")
        print(json.dumps(token_info, indent=2))
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        return False


def test_pod_configurations():
    """Test POD1 and POD2 configurations from .env file"""
    from config import get_pod_config
    
    print("\n" + "=" * 60)
    print("Testing POD Configurations")
    print("=" * 60)
    
    for pod_num in [1, 2]:
        try:
            print(f"\n[POD{pod_num}] Loading configuration...")
            config = get_pod_config(pod_num)
            auth = OpsRampAuth(**config)
            token_info = auth.get_token()
            print(f"✓ POD{pod_num} authenticated successfully!")
            print(f"   Base URL: {config['base_url']}")
            print(f"   Token: {token_info['access_token'][:20]}...")
        except ValueError as e:
            print(f"✗ POD{pod_num} configuration missing")
            print(f"   {str(e)}")
        except Exception as e:
            print(f"✗ POD{pod_num} authentication failed: {str(e)}")


if __name__ == "__main__":
    # Run basic test
    success = test_authentication()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Tests failed - check your .env file")
    print("=" * 60)
    
    # Test POD configurations
    print("\n")
    test_pod_configurations()
