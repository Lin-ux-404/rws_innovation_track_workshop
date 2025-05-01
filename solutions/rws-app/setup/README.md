# Setup

We can start setting up the environment for the following labs.

## Prerequisites

- [Python 3.11](https://www.python.org/downloads/release/python-3113/) is required for this hackathon. We recommend this specific version for compatibility with Azure Functions.

    **Windows Installation using command line:**
    ```powershell
    # Using winget
    winget install Python.Python.3.11
    
    # Or using Chocolatey
    choco install python --version=3.11.4
    ```
    
    **macOS Installation using command line:**
    ```sh
    # Using Homebrew
    brew install python@3.11
    ```
    
    **Linux Installation using command line:**
    ```sh
    # For Ubuntu/Debian
    sudo apt update
    sudo apt install python3.11 python3.11-venv
    ```

    After installation, verify your Python version:
    ```sh
    python --version
    # Or 
    python3.11 --version
    ```
    
    Verify that pip is installed (should be included with Python 3.11):
    ```sh
    # On Windows
    python -m pip --version
    
    # On macOS/Linux
    python3 -m pip --version
    ```
    
    If pip is not available, you can install it with:
    ```sh
    # On Windows
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    
    # On macOS/Linux
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    ```
- (TO-BE-CHECKED)

    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # Or source .venv/bin/activate  # On macOS/Linux
    ```

- Install the python requirements (we'll need them in the following chapters):

    ```sh
    pip install -r shared/requirements.txt
    ```

- [VS Code](https://code.visualstudio.com/) installed with the [Jupyter notebook extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) enabled.
  - Open VS Code, go to “Extensions” (Ctrl+Shift+X or Cmd+Shift+X).
  - Search for 'Jupyter' and click Install.
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed. Check installation:

    ```sh
    az --version
    ```

- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#install-the-azure-functions-core-tools) installed:

  ```sh
  # To install with npm
  npm i -g azure-functions-core-tools@4

  # To install with chocolatey
  choco install azure-functions-core-tools

  # After installation, verify that the tools are working:
  func --version
  ```

- [Sign in to Azure with Azure CLI](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively).
  - To sign in interactively, use the az login command:

    ```sh
    az login
    ```

  - Beginning with Azure CLI version 2.61.0, if you have access to multiple subscriptions, you're prompted to select an Azure subscription. Select the "xyz" subscription for this Hackathon.

### 🚀 Get started

Proceed by opening the Jupyter notebook for the initial [setup](./setup.ipynb), and follow the steps provided.
