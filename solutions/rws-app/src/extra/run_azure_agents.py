import os
import asyncio
from dotenv import load_dotenv

# Import our API Management plugin (to create tools for Azure AI Agents)
from api_plugin import ApiManagementPlugin
from azure_ai_agent import (
    create_data_analyst_azure_agent,
    create_environmental_expert_azure_agent,
    create_business_advisor_azure_agent
)
from utils import check_and_load_environment, display_environment_variables

async def test_azure_agent(agent, prompt):
    """Test an individual Azure AI Agent with a prompt.
    
    Args:
        agent: The Azure AI Agent to test
        prompt: The prompt to send to the agent
    """
    print(f"\n=== Testing Azure Agent: {agent.assistant_params.get('display_name', 'Unknown')} ===\n")
    print(f"User: {prompt}\n")
    
    # Get response from the agent
    response = await agent.invoke(prompt=prompt)
    
    print(f"Agent: {response}\n")
    print("=== Test Complete ===\n")
    
    return response

async def azure_agent_collaboration(agents, prompt):
    """Run a multi-turn conversation with multiple Azure AI Agents.
    
    This is a simple implementation where agents take turns responding to the same prompt.
    In a more sophisticated implementation, you would pass outputs from one agent as input to the next.
    
    Args:
        agents: List of Azure AI Agents
        prompt: The initial prompt to start the conversation
    """
    print(f"\n=== Beginning Azure Agent Collaboration ===\n")
    print(f"User: {prompt}\n")
    
    all_responses = []
    
    # First round: Each agent responds to the original prompt
    for agent in agents:
        agent_name = agent.assistant_params.get('display_name', 'Unknown')
        print(f"\n## {agent_name}'s Analysis:\n")
        
        response = await agent.invoke(prompt=prompt)
        all_responses.append((agent_name, response))
        print(response)
    
    # Create a summary prompt that includes all agent responses
    summary_prompt = f"Original question: {prompt}\n\n"
    for agent_name, response in all_responses:
        summary_prompt += f"{agent_name}'s analysis:\n{response}\n\n"
    
    summary_prompt += "Based on all these analyses, provide a comprehensive answer to the original question."
    
    # Final round: Business Advisor synthesizes all insights
    advisor = [a for a in agents if a.assistant_params.get('display_name') == 'BusinessAdvisor'][0]
    print("\n## Final Synthesis:\n")
    final_response = await advisor.invoke(prompt=summary_prompt)
    print(final_response)
    
    print("\n=== Agent Collaboration Complete ===\n")
    return final_response

async def main():
    """Main entry point for the Azure AI Agent demonstration."""
    # Ensure environment variables are loaded
    check_and_load_environment()
    display_environment_variables()
    
    # Create API functions that can be used as tools
    apim_plugin = ApiManagementPlugin()
    
    # Define tools based on API Management functions
    # This would normally be done by registering the functions with the Azure AI Agent Service
    # Here we're just conceptually showing what tools would be available
    available_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for (city name)"
                        },
                        "unit": {
                            "type": "string",
                            "description": "Temperature unit: 'celsius' or 'fahrenheit'",
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_sql_query",
                "description": "Execute a SQL query against the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_sales_by_region",
                "description": "Get sales data for a specific region",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region_name": {
                            "type": "string",
                            "description": "Optional name of the region to filter by"
                        }
                    }
                }
            }
        }
    ]
    
    # Create specialized Azure AI Agents
    print("\nCreating specialized Azure AI Agents...")
    data_analyst = create_data_analyst_azure_agent(tools=available_tools)
    environmental_expert = create_environmental_expert_azure_agent(tools=[available_tools[0]])  # Only weather tool
    business_advisor = create_business_advisor_azure_agent()  # No tools, just synthesizes information
    
    # Store all agents in a list for convenience
    azure_agents = [data_analyst, environmental_expert, business_advisor]
    
    # Test individual Azure AI Agents
    print("\nTesting individual Azure AI Agents...")
    await test_azure_agent(data_analyst, "Show me the total sales for each region.")
    await test_azure_agent(environmental_expert, "What's the current weather in Amsterdam and how might it affect crop growth?")
    await test_azure_agent(business_advisor, "Given the current sales trends and weather conditions, what strategic actions should we consider?")
    
    # Run a simple Azure AI Agent collaboration
    strategic_query = "How should we adapt our planting and distribution strategies for tomato seeds in Europe next season given current sales data and environmental trends?"
    
    print("\nRunning Azure AI Agent collaboration...")
    await azure_agent_collaboration(azure_agents, strategic_query)

if __name__ == "__main__":
    asyncio.run(main())
