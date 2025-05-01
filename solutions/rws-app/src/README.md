# RWS Multi-Agent System with Semantic Kernel

This directory contains the implementation code for the RWS multi-agent architecture workshop. The code is organized into several Python modules that are referenced from the workshop Jupyter notebook.

## Structure

- `kernel_setup.py` - Functions for setting up the Semantic Kernel and AI services
- `api_plugin.py` - API Management Plugin for connecting to backend services
- `agents.py` - Specialized agent definitions for data analysis, weather, and business advice
- `collaboration.py` - Functions for agent collaboration and multi-agent orchestration
- `utils.py` - Utility functions for environment setup and display
- `run_app.py` - Main script that demonstrates the complete multi-agent system
- `requirements.txt` - Required Python packages

## Setup

1. Create a `.env` file with the following variables:
   ```
   AZURE_OPENAI_ENDPOINT='[YOUR_ENDPOINT]'
   AZURE_OPENAI_API_KEY='[YOUR_API_KEY]'
   AZURE_OPENAI_MODEL_DEPLOYMENT_NAME='gpt-4o'
   APIM_GATEWAY_URL='[YOUR_APIM_GATEWAY_URL]'
   APIM_SUBSCRIPTION_KEY='[YOUR_SUBSCRIPTION_KEY]'
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the example application:
   ```
   python run_app.py
   ```

## Integration with Jupyter Notebook

The code in this directory is designed to be imported and used from the workshop Jupyter notebook. To integrate with the notebook, import the modules as needed:

```python
# Import from the RWS app modules
import sys
import os

# Add the rws-app directory to the Python path
sys.path.append(os.path.abspath('./rws-app'))

# Now import the modules
from kernel_setup import create_kernel_with_service
from api_plugin import ApiManagementPlugin
from agents import create_data_analyst_agent, create_environmental_expert_agent, create_business_advisor_agent
from collaboration import test_agent, create_sequential_group, create_fixed_workflow_chat, run_group_chat
from utils import check_and_load_environment, display_environment_variables
```

Then use the imported functions and classes to build your multi-agent system as demonstrated in the notebook.
