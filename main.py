"""
OpsRamp Template Cloning Tool
Automates cloning of templates from POD-1 to POD-2

Workflow:
=========
POD-1 (Source):
    1. Authenticate
    2. Get global template ID by name
    3. Get cloned template ID using global template ID as parent
    4. Get customizations (JSON body) of the cloned template

POD-2 (Destination):
    1. Authenticate
    2. Get global template ID by same name
    3. Clone template using payload from POD-1
       (replace 'id' with 'clonedTemplateId', use POD-2's global template ID)
"""
import sys
import json
from pathlib import Path

# Ensure imports work correctly
sys.path.insert(0, str(Path(__file__).parent))

from auth.auth import OpsRampAuth
from auth.config import load_env_file, get_pod_config, get_tenant_ids
from config.settings import load_template_names
from global_template.global_template import GlobalTemplateManager
from cloned_template.cloned_template import ClonedTemplateManager
from template_customizations.template_customizations import TemplateCustomizationsManager
from clone_template.clone_template import CloneTemplateManager


def main():
    """Main entry point for the template cloning tool."""
    
    print("=" * 80)
    print("OpsRamp Template Cloning Tool - POD1 to POD2")
    print("=" * 80)
    
    # Load environment variables
    load_env_file()
    
    # ========================================================================
    # STEP 1: Load Template Names from Config
    # ========================================================================
    print("\n[Step 1] Loading template names from config...")
    try:
        template_names = load_template_names()
        print(f"  ✓ Found {len(template_names)} template(s) to process:")
        for idx, name in enumerate(template_names, 1):
            print(f"    {idx}. {name}")
    except (FileNotFoundError, ValueError) as e:
        print(f"  ✗ Error: {str(e)}")
        return
    
    # ========================================================================
    # PART 1: POD-1 (Source)
    # ========================================================================
    print("\n" + "=" * 80)
    print("PART 1: POD-1 (Source)")
    print("=" * 80)
    
    # STEP 2: Authenticate with POD-1
    print("\n[Step 2] Authenticating with POD-1...")
    try:
        pod1_config = get_pod_config(1)
        pod1_tenant_ids = get_tenant_ids(1)
        pod1_tenant_id = pod1_tenant_ids.get('partner_id') or pod1_tenant_ids.get('client_id')
        
        if not pod1_tenant_id:
            print("  ✗ POD1 tenant ID not found in .env file")
            return
        
        pod1_auth = OpsRampAuth(**pod1_config)
        pod1_auth.get_token()
        print("  ✓ Authenticated with POD-1")
        print(f"  ✓ Tenant ID: {pod1_tenant_id}")
    except Exception as e:
        print(f"  ✗ Authentication failed: {str(e)}")
        return
    
    # Store results for each template
    pod1_results = {}
    
    for template_name in template_names:
        print(f"\n  Processing: {template_name}")
        print("  " + "-" * 60)
        
        # STEP 3: Get Global Template ID from POD-1
        print("\n  [Step 3] Getting global template ID...")
        global_mgr = GlobalTemplateManager(pod1_auth, pod1_tenant_id)
        global_template_info = global_mgr.get_global_template_by_name(template_name)
        
        if not global_template_info:
            print(f"    ✗ Global template not found: {template_name}")
            continue
        
        print(f"    ✓ Global Template ID: {global_template_info.template_id}")
        
        # STEP 4: Get Cloned Template ID using Global Template ID as parent
        print("\n  [Step 4] Getting cloned template ID...")
        cloned_mgr = ClonedTemplateManager(pod1_auth, pod1_tenant_id)
        cloned_template_info = cloned_mgr.get_cloned_template_by_parent_id(
            global_template_info.template_id
        )
        
        if not cloned_template_info:
            print(f"    ✗ No cloned template found for parent: {global_template_info.template_id}")
            continue
        
        print(f"    ✓ Cloned Template ID: {cloned_template_info.template_id}")
        print(f"    ✓ Cloned Template Name: {cloned_template_info.name}")
        print(f"    ✓ Scope: {cloned_template_info.scope}")
        
        # STEP 5: Get Customizations (JSON body) of the cloned template
        print("\n  [Step 5] Getting template customizations...")
        customizations_mgr = TemplateCustomizationsManager(pod1_auth, pod1_tenant_id)
        customizations = customizations_mgr.get_template_customizations(
            cloned_template_info.template_id
        )
        
        if not customizations:
            print("    ✗ Failed to get template customizations")
            continue
        
        print("    ✓ Customizations retrieved successfully")
        
        # Save customizations to file
        safe_filename = template_name.replace(' ', '_').replace('/', '-')[:50]
        customizations_mgr.save_customizations_to_file(
            customizations, 
            f"pod1_{safe_filename}_customizations.json"
        )
        
        # Store results for POD-2 processing
        pod1_results[template_name] = {
            'global_template_id': global_template_info.template_id,
            'cloned_template_id': cloned_template_info.template_id,
            'customizations': customizations
        }
    
    if not pod1_results:
        print("\n✗ No templates processed from POD-1. Exiting.")
        return
    
    # ========================================================================
    # PART 2: POD-2 (Destination)
    # ========================================================================
    print("\n" + "=" * 80)
    print("PART 2: POD-2 (Destination)")
    print("=" * 80)
    
    # STEP 6: Authenticate with POD-2
    print("\n[Step 6] Authenticating with POD-2...")
    try:
        pod2_config = get_pod_config(2)
        pod2_tenant_ids = get_tenant_ids(2)
        pod2_tenant_id = pod2_tenant_ids.get('partner_id') or pod2_tenant_ids.get('client_id')
        
        if not pod2_tenant_id:
            print("  ✗ POD2 tenant ID not found in .env file")
            return
        
        pod2_auth = OpsRampAuth(**pod2_config)
        pod2_auth.get_token()
        print("  ✓ Authenticated with POD-2")
        print(f"  ✓ Tenant ID: {pod2_tenant_id}")
    except Exception as e:
        print(f"  ✗ Authentication failed: {str(e)}")
        return
    
    # Process each template
    clone_results = {}
    
    for template_name, pod1_data in pod1_results.items():
        print(f"\n  Processing: {template_name}")
        print("  " + "-" * 60)
        
        # STEP 7: Get Global Template ID from POD-2
        print("\n  [Step 7] Getting global template ID from POD-2...")
        global_mgr_pod2 = GlobalTemplateManager(pod2_auth, pod2_tenant_id)
        global_template_info_pod2 = global_mgr_pod2.get_global_template_by_name(template_name)
        
        if not global_template_info_pod2:
            print(f"    ✗ Global template not found in POD-2: {template_name}")
            continue
        
        print(f"    ✓ Global Template ID (POD-2): {global_template_info_pod2.template_id}")
        
        # STEP 8: Clone template to POD-2
        print("\n  [Step 8] Cloning template to POD-2...")
        clone_mgr = CloneTemplateManager(pod2_auth, pod2_tenant_id)
        
        # Prepare new name for cloned template (optional)
        new_name = f"MSE Template Test - {template_name}"
        
        clone_response = clone_mgr.clone_template(
            source_customizations=pod1_data['customizations'],
            target_global_template_id=global_template_info_pod2.template_id,
            new_template_name=new_name
        )
        
        if clone_response:
            # Save clone response
            safe_filename = template_name.replace(' ', '_').replace('/', '-')[:50]
            clone_mgr.save_clone_response(
                clone_response,
                f"pod2_{safe_filename}_clone_response.json"
            )
            
            clone_results[template_name] = {
                'pod2_global_template_id': global_template_info_pod2.template_id,
                'new_cloned_template_id': clone_response.get('id'),
                'success': True
            }
        else:
            clone_results[template_name] = {
                'pod2_global_template_id': global_template_info_pod2.template_id,
                'success': False
            }
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print("\nPOD-1 Results:")
    for name, data in pod1_results.items():
        print(f"  • {name}")
        print(f"    Global Template ID: {data['global_template_id']}")
        print(f"    Cloned Template ID: {data['cloned_template_id']}")
    
    print("\nPOD-2 Clone Results:")
    for name, data in clone_results.items():
        status = "✓ Success" if data.get('success') else "✗ Failed"
        print(f"  • {name}: {status}")
        if data.get('new_cloned_template_id'):
            print(f"    New Template ID: {data['new_cloned_template_id']}")
    
    print("\n" + "=" * 80)
    print("Template cloning completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
