# SSE-Opsramp-DMP-clone-library

Python automation tool for cloning OpsRamp templates between POD environments.

## Overview

This tool automates the cloning of OpsRamp monitoring templates from POD-1 (source) to POD-2 (destination). It fetches template customizations from the source POD and clones them to the target POD while preserving configurations.

## Workflow

### POD-1 (Source):

1. Authenticate with POD-1
2. Get global template ID by template name
3. Get cloned template ID using global template ID as parent
4. Get customizations (JSON body) of the cloned template

### POD-2 (Destination):

1. Authenticate with POD-2
2. Get global template ID by the same name
3. Clone template using payload from POD-1 (replace `id` with `clonedTemplateId`)

## Project Structure

```
├── auth/                    # Authentication module
│   ├── auth.py             # OpsRamp OAuth authentication
│   └── config.py           # Environment configuration loader
├── config/                  # Configuration files
│   ├── settings.py         # Settings loader
│   └── template_names.txt  # List of templates to clone
├── global_template/         # Global template module
│   └── global_template.py  # Fetch global template by name
├── cloned_template/         # Cloned template module
│   └── cloned_template.py  # Fetch cloned template by parent ID
├── template_customizations/ # Template customizations module
│   └── template_customizations.py  # Get template JSON payload
├── clone_template/          # Clone template module
│   └── clone_template.py   # Clone template to target POD
├── output/                  # Output directory for JSON files
├── main.py                  # Main orchestration script
└── .env                     # Environment variables (create this)
```

## Setup

### 1. Create Virtual Environment (Recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install requests
```

### 3. Configure Credentials

Create a `.env` file in the project root:

```env
# POD 1 Configuration (Source)
POD1_BASE_URL=https://hpe.api.opsramp.com
POD1_CLIENT_KEY=your_oauth_client_key
POD1_CLIENT_SECRET=your_oauth_client_secret
POD1_CLIENT_ID=your_tenant_id
POD1_PARTNER_ID=your_partner_id

# POD 2 Configuration (Destination)
POD2_BASE_URL=https://preprod.api.opsramp.net
POD2_CLIENT_KEY=your_oauth_client_key
POD2_CLIENT_SECRET=your_oauth_client_secret
POD2_CLIENT_ID=your_tenant_id
POD2_PARTNER_ID=your_partner_id
```

**Note:** `CLIENT_KEY` is for OAuth authentication, `CLIENT_ID`/`PARTNER_ID` is the tenant ID used in API calls.

### 4. Configure Template Names

Edit `config/template_names.txt` to add the global template names you want to clone:

```
# Template Names Configuration
# Add one global template name per line
hpe-alletra Alletra 9000 HPE Alletra Battery Template - 9
hpe-alletra Alletra MP HPE Alletra Array Template - 5
```

## Usage

### Running the Main Tool

```powershell
python main.py
```

This will execute the complete workflow:

1. Load template names from `config/template_names.txt`
2. **POD-1**: Authenticate, get global template ID, get cloned template ID, get customizations
3. **POD-2**: Authenticate, get global template ID, clone template with customizations

### Output Files

The tool saves JSON files in the `output/` directory:

- `pod1_{template_name}_customizations.json` - Template customizations from POD-1
- `pod2_{template_name}_clone_response.json` - Clone API response from POD-2

## API Integration Examples

### Using Global Template Module

```python
from auth.auth import OpsRampAuth
from auth.config import get_pod_config, get_tenant_ids
from global_template.global_template import GlobalTemplateManager

# Setup
pod_config = get_pod_config(1)
tenant_ids = get_tenant_ids(1)
auth = OpsRampAuth(**pod_config)
tenant_id = tenant_ids.get('partner_id')

# Get global template by name
manager = GlobalTemplateManager(auth, tenant_id)
template_info = manager.get_global_template_by_name(
    "hpe-alletra Alletra 9000 HPE Alletra Battery Template - 9"
)
print(f"Template ID: {template_info.template_id}")
```

### Using Cloned Template Module

```python
from cloned_template.cloned_template import ClonedTemplateManager

# Get cloned template using global template ID as parent
manager = ClonedTemplateManager(auth, tenant_id)
cloned_info = manager.get_cloned_template_by_parent_id(global_template_id)
print(f"Cloned Template ID: {cloned_info.template_id}")
```

### Using Template Customizations Module

```python
from template_customizations.template_customizations import TemplateCustomizationsManager

# Get full template customizations (JSON payload)
manager = TemplateCustomizationsManager(auth, tenant_id)
customizations = manager.get_template_customizations(cloned_template_id)
```

### Using Clone Template Module

```python
from clone_template.clone_template import CloneTemplateManager

# Clone template to POD-2
manager = CloneTemplateManager(pod2_auth, pod2_tenant_id)
response = manager.clone_template(
    source_customizations=customizations,
    target_global_template_id=pod2_global_template_id,
    new_template_name="My Cloned Template"
)
print(f"New Template ID: {response.get('id')}")

# Get authorization header for API requests
headers = auth.get_auth_header()
# Returns: {'Authorization': 'Bearer <token>'}
```

### Fetching Integration Details

```python
from integration.integration import IntegrationManager

integration_mgr = IntegrationManager(auth, tenant_id)
integrations = integration_mgr.get_integration_details(app_name="alletra")

for integration in integrations:
    print(f"App: {integration.app_name}")
    print(f"Version: {integration.version}")
    print(f"Native Types: {integration.native_types}")
    print(f"Persona: {integration.persona}")
```

### Fetching Templates

```python
from templates.templates import TemplateManager

template_mgr = TemplateManager(auth, tenant_id)
templates = template_mgr.get_global_template_ids(integration)

for template in templates:
    print(f"Template ID: {template.template_id}")
    print(f"Name: {template.name}")
    print(f"Native Type: {template.native_type}")
```

### Fetching Cloned Templates

```python
from cloned_templates.cloned_templates import ClonedTemplateManager

cloned_mgr = ClonedTemplateManager(auth, tenant_id)
cloned_dict = cloned_mgr.get_all_cloned_templates(all_templates)

# cloned_dict maps: global_template_id -> List[ClonedTemplateInfo]
for global_id, clones in cloned_dict.items():
    print(f"Parent Global Template: {global_id}")
    for clone in clones:
        print(f"  → Cloned Template: {clone.template_id}")
```

## Features

### Current Implementation

#### 1. Authentication Module (`auth/`)

- ✅ OAuth2 client credentials flow
- ✅ Automatic token caching and refresh
- ✅ 60-second expiration buffer for safety
- ✅ Configuration management via `.env` file

#### 2. Integration Discovery (`integration/`)

- ✅ Search integrations by name (e.g., "alletra")
- ✅ Extract app names, versions, native types
- ✅ Parse persona from metadata hierarchy

#### 3. Template Management (`templates/`)

- ✅ Fetch global template IDs
- ✅ Filter by app name, native type, version, persona
- ✅ Handle multiple native types per integration

#### 4. Cloned Template Discovery (`cloned_templates/`)

- ✅ Fetch cloned templates using parent global template IDs
- ✅ Map clones to their parent templates
- ✅ Support multiple scopes (GLOBAL, SERVICE PROVIDER, CLIENT, PARTNER)

### Planned Features

- ⏳ Get customizations using cloned template ID
- ⏳ Clone DMPs and templates to POD2
- ⏳ Update cloned template customizations
- ⏳ Bulk cloning operations

## Project Structure

```
SSE-Opsramp-DMP-clone-library/
├── auth/
│   ├── auth.py              # OAuth2 authentication with token caching
│   ├── config.py            # .env configuration loader
│   └── auth_test.py         # Authentication component test
├── integration/
│   ├── integration.py       # Integration discovery (apps, versions, types)
│   └── integration_test.py  # Integration component test
├── templates/
│   ├── templates.py         # Global template ID fetching
│   └── templates_test.py    # Template component test
├── cloned_templates/
│   ├── cloned_templates.py  # Cloned template discovery
│   └── cloned_templates_test.py  # Cloned template component test
├── sample_jsons/            # API response samples (gitignored)
├── .env                     # Credentials (gitignored)
├── .env.example             # Credentials template
├── .gitignore
├── main.py                  # Main orchestration script
├── LICENSE
└── README.md
```

### Component Architecture

Each component follows a consistent pattern:

- **Data Class**: Stores structured information (e.g., `IntegrationInfo`, `TemplateInfo`)
- **Manager Class**: Handles API interactions and business logic
- **Test Script**: Standalone testing for the component

## Workflow

The tool executes the following steps:

### Discovery Phase (Current)

1. **Configuration Loading**
   - Read credentials from `.env` file
   - Validate required configuration values

2. **Authentication**
   - Obtain OAuth2 access token
   - Cache token with automatic refresh

3. **Integration Discovery**
   - Search for integrations by name
   - Extract app metadata (name, version, native types, persona)

4. **Global Template Discovery**
   - For each integration and native type combination
   - Fetch global template IDs from OpsRamp API
   - Build queryString filters: `scope:GLOBAL+appName+nativeType+version+name`

5. **Cloned Template Discovery**
   - For each global template ID
   - Find cloned templates using `parentId` filter
   - Map clones to their parent global templates

### Cloning Phase (To Be Implemented)

6. **Get Customizations**
   - Fetch customization details from cloned templates in POD1

7. **Clone to POD2**
   - Authenticate with POD2
   - Clone global templates for target tenants
   - Clone DMPs for target tenants
   - Apply customizations to cloned templates

8. **Verification**
   - Validate cloned resources
   - Run DMPs (optional)

## Troubleshooting

### SSL Certificate Warnings

SSL verification is disabled for development environments:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

For production, configure proper SSL certificates.

### Authentication Errors

- Verify `CLIENT_KEY` and `CLIENT_SECRET` in `.env` are correct
- Ensure they are different values (common mistake: both set to same value)
- Check the base URL matches your OpsRamp environment
- Confirm credentials have required API permissions

### Configuration Issues

- Ensure `.env` file exists in project root
- Verify all required fields are populated
- `CLIENT_KEY` = OAuth client key (for authentication)
- `CLIENT_ID` = Tenant ID (for API calls)

### Import Errors

If running scripts from subdirectories, they use:

```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

to resolve parent module imports.

### API Response Issues

- Check if `resourceHierarchy` in API response is dict or string
- Persona extraction handles both types automatically
- Some global templates may have 0 cloned templates (expected)

## Development Notes

### Python Version

- Developed with Python 3.13.5
- Compatible with Python 3.7+

### Code Style

- Type hints for function parameters and returns
- Dataclasses for structured information
- Manager pattern for API interactions
- Modular component architecture

### Testing

Each component has a standalone test script:

- Tests can run independently without main.py
- Useful for debugging specific functionality
- Follows same workflow as main integration
