import os
from semantic_kernel.connectors.ai.open_ai import AzureOpenAIAgent

class AzureAgentFactory:
    """Factory class for creating Azure AI Agents."""
    
    @staticmethod
    def create_azure_agent(display_name, description, instructions, tools=None):
        """Create an Azure AI Agent with the specified configuration.
        
        Args:
            display_name: The name to display for the agent
            description: A short description of the agent's purpose
            instructions: Detailed instructions for the agent
            tools: Optional list of tools available to the agent
            
        Returns:
            An Azure AI Agent instance
        """
        # Ensure environment variables are loaded
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME")
        
        if not endpoint or not api_key or not deployment:
            raise ValueError("AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_MODEL_DEPLOYMENT_NAME must be set")
        
        # Create the Azure AI Agent
        agent = AzureOpenAIAgent(
            endpoint=endpoint,
            api_key=api_key,
            deployment_name=deployment,
            api_version="2024-02-15-preview",
            assistant_params={
                "display_name": display_name,
                "description": description,
                "instructions": instructions,
                "tools": tools or []
            }
        )
        
        return agent

def create_data_analyst_azure_agent(tools=None):
    """Create a Data Analyst Azure AI Agent."""
    return AzureAgentFactory.create_azure_agent(
        display_name="DataAnalyst",
        description="A data analyst that specializes in analyzing sales data",
        instructions="""You are a data analyst expert who specializes in analyzing sales data and providing insights.
        
        Your responsibilities:
        - Query the SQL database to retrieve sales data
        - Analyze patterns and trends in the data
        - Identify key insights about sales performance
        - Provide clear explanations of your findings
        - Use the available functions to access data rather than making assumptions
        
        Always structure your analysis logically and explain your reasoning. When appropriate, suggest follow-up queries that might provide additional insights.
        
        Be concise and focus on the most important information.
        """,
        tools=tools
    )

def create_environmental_expert_azure_agent(tools=None):
    """Create an Environmental Expert Azure AI Agent."""
    return AzureAgentFactory.create_azure_agent(
        display_name="EnvironmentalExpert",
        description="An environmental expert that specializes in weather conditions and agricultural impacts",
        instructions="""You are an environmental expert who specializes in weather conditions and their impact on agricultural operations.
        
        Your responsibilities:
        - Retrieve current weather information for relevant locations
        - Interpret weather conditions and their implications
        - Provide insights on how weather might affect agricultural activities
        - Use the available functions to get real-time data rather than making assumptions
        
        Be concise and provide practical insights based on the weather information you retrieve.
        """,
        tools=tools
    )

def create_business_advisor_azure_agent(tools=None):
    """Create a Business Advisor Azure AI Agent."""
    return AzureAgentFactory.create_azure_agent(
        display_name="BusinessAdvisor",
        description="A business advisor that provides strategic recommendations",
        instructions="""You are a business advisor who provides strategic recommendations based on data analysis and environmental factors.
        
        Your responsibilities:
        - Synthesize information from data analysis and environmental conditions
        - Identify business opportunities and risks
        - Suggest strategic actions based on the available information
        - Provide a balanced view considering multiple factors
        - Focus on practical, actionable recommendations
        
        Your recommendations should be clear, specific, and directly relevant to agricultural operations.
        """,
        tools=tools
    )
