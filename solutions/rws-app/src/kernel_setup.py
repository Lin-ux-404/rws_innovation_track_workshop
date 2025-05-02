import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior

def create_kernel_with_service(service_id, temperature=0.7):
    """Create a kernel with a chat completion service.
    
    Args:
        service_id: The service ID to use for the AI service
        temperature: The temperature to use for the AI service (0.0 to 1.0)
    
    Returns:
        A configured kernel with the specified service
    """
    
    # Load environment variables if they haven't been loaded yet
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        load_dotenv()
        
    kernel = sk.Kernel()
    
    # Add Azure OpenAI service
    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name=os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME"),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
    )
    
    # Configure settings for the service
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.temperature = temperature
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    return kernel
