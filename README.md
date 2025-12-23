# SSE-Opsramp-DMP-clone-library

Shared Services' Opsramp DMP cloning library package

## Overview

Automates the process of cloning templates and DMPs from one OpsRamp POD to another.

## Setup

### 1. Install Dependencies

```powershell
pip install requests
```

### 2. Configure Credentials

**Option A: Environment Variables (Recommended)**

```powershell
$env:POD1_CLIENT_ID = "your_pod1_key"
$env:POD1_CLIENT_SECRET = "your_pod1_secret"
$env:POD2_CLIENT_ID = "your_pod2_key"
$env:POD2_CLIENT_SECRET = "your_pod2_secret"
```

**Option B: Direct in Code (Testing Only)**
Edit the credentials directly in `auth_test.py` or `main.py`

## Usage

### Testing Authentication

**Quick Test:**

```powershell
cd "c:\Users\ahmedama\Documents\HPE Projects\SSE-Opsramp-DMP-clone-library"
python auth\auth_test.py
```

Edit `auth\auth_test.py` and replace:

- `your_client_id_here` with your actual client ID
- `your_client_secret_here` with your actual client secret

**Using Environment Variables:**

```powershell
$env:OPSRAMP_CLIENT_ID = "your_key"
$env:OPSRAMP_CLIENT_SECRET = "your_secret"
python auth\auth_test.py
```

### Running the Main Application

```powershell
python main.py
```

### Using in Your Own Code

```python
from auth.auth import OpsRampAuth

# Initialize
auth = OpsRampAuth(
    base_url='https://hpe-dev.api.try.opsramp.com',
    client_id='your_key',
    client_secret='your_secret'
)

# Get token (automatically cached and refreshed)
token_info = auth.get_token()
print(f"Access Token: {token_info['access_token']}")

# Get authorization header for API requests
headers = auth.get_auth_header()
# Returns: {'Authorization': 'Bearer <token>'}

# Use in API requests
import requests
response = requests.get(
    'https://hpe-dev.api.try.opsramp.com/api/v2/tenants',
    headers=headers
)
```

## Features

### Authentication (`auth/auth.py`)

- ✅ OAuth2 client credentials flow
- ✅ Automatic token caching
- ✅ Automatic token refresh on expiration
- ✅ Clean API interface

### Token Management

- Tokens are cached and reused until expiration
- Automatic refresh with 60-second safety buffer
- Thread-safe token management

## Project Structure

```
SSE-Opsramp-DMP-clone-library/
├── auth/
│   ├── auth.py          # Authentication module
│   └── auth_test.py     # Test script
├── main.py              # Main application entry point
├── sample_jsons/        # Sample JSON files
└── README.md            # This file
```

## Cloning Process (To Be Implemented)

1. **Fetch template customizations from POD1**

   - Generate tenant credentials in POD1
   - Get app name, version, native type(s), and persona
   - Get the global template ID
   - Get the cloned template ID using the global template ID
   - Get customizations using the cloned template ID

2. **Clone DMP and templates to POD2**
   - Generate tenant credentials in POD2
   - Get List of Partner OR Client IDs
   - Get the global template ID
   - Clone the global template for the tenant
   - Get the global DMP ID
   - Clone the global DMP for the tenant
   - Run the cloned DMP (optional)
   - Update cloned template customizations

## Troubleshooting

### SSL Certificate Warnings

The current implementation uses `verify=False` for SSL verification. For production, consider:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### Authentication Errors

- Verify your client ID and secret are correct
- Check the base URL matches your OpsRamp environment
- Ensure your credentials have the required permissions

### Token Expiration

Tokens automatically refresh. If you encounter issues:

```python
auth.refresh_token()  # Force refresh
```
