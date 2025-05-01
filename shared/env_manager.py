import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils import print_info, print_error, print_ok

# Store the .env.json file in the same directory as env_manager.py
ENV_FILE_PATH = os.path.join(str(Path(__file__).parent), '.env.json')

def save_variables(variables: Dict[str, Any], filepath: Optional[str] = None) -> str:
    """
    Save variables to a JSON file that can be loaded by other notebooks.
    
    Args:
        variables: Dictionary of variables to save
        filepath: Optional custom filepath to save variables to
        
    Returns:
        Path to the saved file
    """
    filepath = filepath or ENV_FILE_PATH
    
    try:
        # Make sure parent directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Read existing variables if file exists
        existing_vars = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing_vars = json.load(f)
        
        # Update with new variables
        existing_vars.update(variables)
        
        # Write back to file
        with open(filepath, 'w') as f:
            json.dump(existing_vars, f, indent=2)
            
        print_ok(f"Variables saved to {filepath}")
        return filepath
    except Exception as e:
        print_error(f"Failed to save variables: {str(e)}")
        return ""

def load_variables(filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    Load variables from a JSON file.
    
    Args:
        filepath: Optional custom filepath to load variables from
        
    Returns:
        Dictionary of variables
    """
    filepath = filepath or ENV_FILE_PATH
    
    if not os.path.exists(filepath):
        print_info(f"No variables file found at {filepath}")
        return {}
        
    try:
        with open(filepath, 'r') as f:
            variables = json.load(f)
        print_ok(f"Loaded {len(variables)} variables from {filepath}")
        return variables
    except Exception as e:
        print_error(f"Failed to load variables: {str(e)}")
        return {}

def get_variable(key: str, default: Any = None, filepath: Optional[str] = None) -> Any:
    """
    Get a single variable from the saved variables.
    
    Args:
        key: Variable name to retrieve
        default: Default value if variable doesn't exist
        filepath: Optional custom filepath to load variables from
        
    Returns:
        Variable value or default if not found
    """
    variables = load_variables(filepath)
    return variables.get(key, default)

def get_variable_with_default(var_name: Any, caller_globals, default=None, verbose=False):
    """
    Get a variable from the caller's scope or from the environment variables file if not defined.
    
    Args:
        var_name: Name of the variable to retrieve
        caller_globals: The globals() dictionary from the caller's scope
        default: Default value if not found in either scope or environment
        verbose: Whether to print information messages
        
    Returns:
        The value of the variable from scope, environment, or default    """
    
    # Check if the variable is already defined in the caller's scope
    if var_name in caller_globals and caller_globals[var_name] is not None:
        if verbose:
            print_info(f"Using existing {var_name} from notebook: {caller_globals[var_name]}")
        return caller_globals[var_name]
    else:
        # Load variable from environment file
        variables = load_variables()
        value = variables.get(var_name, default)
        
        if value is not None:
            if verbose:
                print_info(f"Loaded {var_name} from environment file: {value}")
        elif default is not None:
            if verbose:
                print_info(f"Using default value for {var_name}: {default}")
            value = default
        else:
            if verbose:
                print_warning(f"Variable {var_name} not found in notebook scope or environment file")
                
        return value

def update_notebook_env(variables: Dict[str, Any] = None, filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    Load variables and update the notebook environment.
    This function both loads variables and updates os.environ with them.
    
    Args:
        variables: Optional new variables to save before loading
        filepath: Optional custom filepath to load/save variables
        
    Returns:
        Dictionary of all variables (loaded + new)
    """
    if variables:
        save_variables(variables, filepath)
        
    loaded_vars = load_variables(filepath)
    
    # Update environment variables
    for key, value in loaded_vars.items():
        if isinstance(value, str):
            os.environ[key] = value
        else:
            # For non-string values, we'll stringify them for environment variables
            os.environ[key] = str(value)
    
    return loaded_vars
