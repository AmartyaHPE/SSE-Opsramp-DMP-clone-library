"""
Test script for integration module.
Tests fetching and parsing integration details from OpsRamp API.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.integration import IntegrationManager, IntegrationInfo
from auth.auth import OpsRampAuth
from auth.config import get_pod_config
import json


def test_with_sample_json():
    """Test parsing with local sample JSON file"""
    print("=" * 80)
    print("Test 1: Parsing Sample JSON File")
    print("=" * 80)
    
    # Load sample JSON
    with open('../sample_jsons/integration_sample.json', 'r') as f:
        sample_data = json.load(f)
    
    # Create a dummy auth (won't be used for this test)
    auth = OpsRampAuth("https://dummy.com", "dummy", "dummy")
    manager = IntegrationManager(auth, "dummy_client")
    
    # Extract information
    integrations = manager.extract_integration_info(sample_data)
    
    # Print summary
    manager.print_integration_summary(integrations)
    
    # Print detailed JSON
    print("\n📋 Detailed Information (JSON):")
    for info in integrations:
        print(json.dumps(info.to_dict(), indent=2))
        print()
    
    return integrations


def test_with_live_api():
    """Test with live API call"""
    print("\n" + "=" * 80)
    print("Test 2: Fetching from Live API")
    print("=" * 80)
    
    try:
        # Load POD1 configuration
        pod1_config = get_pod_config(1)
        client_id = pod1_config.get('client_id')
        
        # Initialize auth
        print("\n1. Authenticating...")
        auth = OpsRampAuth(**pod1_config)
        token = auth.get_token()
        print(f"   ✓ Authenticated successfully")
        print(f"   Token: {token['access_token'][:20]}...")
        
        # You need to provide the actual client/tenant ID for the API
        # This is different from the OAuth client_id
        tenant_id = input("\n2. Enter Tenant/Client ID (for API endpoint): ").strip()
        
        if not tenant_id:
            print("   ⚠ Skipping live API test (no tenant ID provided)")
            return None
        
        # Initialize Integration Manager
        manager = IntegrationManager(auth, tenant_id)
        
        # Search for alletra integrations
        print("\n3. Searching for 'alletra' integrations...")
        integrations = manager.get_integration_details(app_name="alletra")
        
        # Print results
        manager.print_integration_summary(integrations)
        
        # Save to file
        output_file = '../sample_jsons/integration_output.json'
        with open(output_file, 'w') as f:
            json.dump([info.to_dict() for info in integrations], f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")
        
        return integrations
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        return None
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test with sample JSON
    sample_results = test_with_sample_json()
    
    # Ask if user wants to test with live API
    print("\n" + "=" * 80)
    test_live = input("\nDo you want to test with live API? (y/n): ").strip().lower()
    
    if test_live == 'y':
        live_results = test_with_live_api()
    else:
        print("\n✓ Skipping live API test")
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)
