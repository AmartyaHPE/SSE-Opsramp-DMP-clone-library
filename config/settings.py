from pathlib import Path
from typing import List


def load_template_names(config_file: str = None) -> List[str]:
    
    if config_file is None:
        config_file = Path(__file__).parent / 'template_names.txt'
    else:
        config_file = Path(config_file)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Template names file not found: {config_file}\n"
            "Please create the file and add template names (one per line)."
        )
    
    template_names = []
    
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            template_names.append(line)
    
    if not template_names:
        raise ValueError(
            f"No template names found in {config_file}\n"
            "Please add at least one template name."
        )
    
    return template_names
