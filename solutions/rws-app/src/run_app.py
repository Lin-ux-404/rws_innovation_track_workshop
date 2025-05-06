from dotenv import load_dotenv
import semantic_kernel as sk

from kernel_setup import create_kernel_with_service
from api_plugin import ApiManagementPlugin
from rag_plugin import RAGPlugin
from agents import (
    create_infrastructure_analyst_agent,
    create_water_management_expert_agent,
    create_strategic_advisor_agent,
    create_knowledge_agent,
    create_research_synthesis_agent
)
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from instrumentation import track_agent_action, AgentActionContext
from collaboration import create_sequential_group, run_group_chat

# Load environment variables
load_dotenv()

# Initialize the kernel with Azure OpenAI service
kernel = create_kernel_with_service(service_id="chat-completion", temperature=0.7)
settings = kernel.get_prompt_execution_settings_from_service_id(
    service_id="chat-completion"
)
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Create our specialized agents
infrastructure_analysis_agent = create_infrastructure_analyst_agent(kernel, settings)
water_management_expert_agent = create_water_management_expert_agent(kernel, settings)
strategic_advisor_agent = create_strategic_advisor_agent(kernel, settings)
knowledge_agent = create_knowledge_agent(kernel, settings)
research_synthesis_agent = create_research_synthesis_agent(kernel, settings)

# Store all agents in a list for convenience
agents = [
    infrastructure_analysis_agent,
    water_management_expert_agent,
    strategic_advisor_agent,
    knowledge_agent,
    research_synthesis_agent,
]

print(
    f"Created specialized agents: {', '.join([agent.name for agent in agents])}"
)

# Register plugins
kernel.add_plugins([
    ApiManagementPlugin(), # Custom API management plugin
    RAGPlugin() # RAG plugin for knowledge retrieval
])

sequential_group = create_sequential_group(agents, max_iterations=6)  # 2 rounds of all 3 agents
# Test the sequential group with a complex question
complex_query = "Given the current sales data and weather conditions in Europe, what strategic recommendations can you provide for our agricultural product sales in the next quarter?"

async def main():
    chat_history = await run_group_chat(sequential_group, complex_query)
    print("Chat history:")
    for message in chat_history:
        print(f"{message.role}: {message.content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
