# Loads credentials from .env file.
import os
from pathlib import Path
from typing import Dict, Optional


def load_env_file(env_path: Optional[str] = None) -> None:
    # Load environment variables from .env file.
    
    # Args: env_path: Path to .env file. If None, looks for .env in project root.
    
    if env_path is None:
        # Look for .env in project root
        current_dir = Path(__file__).parent.parent
        env_path = current_dir / '.env'
    else:
        env_path = Path(env_path)
    
    if not env_path.exists():
        print(f"Warning: .env file not found at {env_path}")
        print("Copy .env.example to .env and fill in your credentials")
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Only set if not already in environment
                if key and value and key not in os.environ:
                    os.environ[key] = value


def get_pod_config(pod_number: int) -> Dict[str, str]:

    prefix = f"POD{pod_number}"
    
    base_url = os.getenv(f'{prefix}_BASE_URL')
    client_id = os.getenv(f'{prefix}_CLIENT_ID')
    client_secret = os.getenv(f'{prefix}_CLIENT_SECRET')
    
    if not all([base_url, client_id, client_secret]):
        missing = []
        if not base_url:
            missing.append(f'{prefix}_BASE_URL')
        if not client_id:
            missing.append(f'{prefix}_CLIENT_ID')
        if not client_secret:
            missing.append(f'{prefix}_CLIENT_SECRET')
        
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set them in your .env file or environment."
        )
    
    return {
        'base_url': base_url,
        'client_id': client_id,
        'client_secret': client_secret
    }


def get_default_config() -> Dict[str, str]:
    # for single POD testing
    
    base_url = os.getenv('OPSRAMP_BASE_URL')
    client_id = os.getenv('OPSRAMP_CLIENT_ID')
    client_secret = os.getenv('OPSRAMP_CLIENT_SECRET')
    
    if not all([base_url, client_id, client_secret]):
        missing = []
        if not base_url:
            missing.append('OPSRAMP_BASE_URL')
        if not client_id:
            missing.append('OPSRAMP_CLIENT_ID')
        if not client_secret:
            missing.append('OPSRAMP_CLIENT_SECRET')
        
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set them in your .env file or environment."
        )
    
    return {
        'base_url': base_url,
        'client_id': client_id,
        'client_secret': client_secret
    }


# Auto-load .env file when module is imported
load_env_file()
