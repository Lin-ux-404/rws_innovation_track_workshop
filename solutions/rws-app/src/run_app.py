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
    create_research_synthesis_agent,
)
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from instrumentation import track_agent_action, AgentActionContext
from collaboration import create_sequential_group, run_group_chat

# Import additional required modules for vertical architecture
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.agents.strategies import DefaultTerminationStrategy
from semantic_kernel.agents.strategies.selection.selection_strategy import (
    SelectionStrategy,
)
from semantic_kernel.functions import KernelFunction
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.functions import KernelFunctionFromPrompt

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

print(f"Created specialized agents: {', '.join([agent.name for agent in agents])}")

# Register plugins
kernel.add_plugins(
    [
        ApiManagementPlugin(),  # Custom API management plugin
        RAGPlugin(),  # RAG plugin for knowledge retrieval
    ]
)


# Define a custom selection strategy using KernelFunctionFromPrompt
class LeadAgentSelectionStrategy(SelectionStrategy):
    """
    A lead agent selection strategy that analyzes the query and context to determine
    which specialized agent should respond next.
    """

    def __init__(self, agents):
        """
        Initialize the selection strategy with a kernel and list of available agents.

        Args:
            agents: List of available specialized agents
        """
        super().__init__()
        # Initialize fields directly in __init__ without using self.__dict__
        # to avoid Pydantic validation issues
        self._agents_by_name = {agent.name: agent for agent in agents}
        # Create the agent selection function
        self._agent_selection_function = self._create_agent_selection_function()

    def _create_agent_selection_function(self):
        """Create a kernel function to select the next agent."""
        prompt = """
        You are a lead agent coordinator responsible for analyzing a conversation and determining which specialized agent should respond next.
        
        Available agents:
        - InfrastructureAnalyst: Specializes in analyzing infrastructure assets and safety conditions, using data on critical infrastructure, safety inspections, maintenance projects, and recommending improvements.
        - WaterManagementExpert: Specializes in Dutch water infrastructure and flood protection systems, analyzing flood defense systems, water level monitoring, and emergency preparedness.
        - StrategicAdvisor: Provides long-term infrastructure recommendations, synthesizing information from infrastructure analysis and water management, identifying strategic opportunities/risks.
        - KnowledgeAgent: Retrieves and synthesizes information from the knowledge base about Dutch infrastructure and water management, searching for relevant documents and technical reports.
        - ResearchSynthesisAgent: Combines historical knowledge with current infrastructure data, analyzing historical performance, comparing past/current maintenance approaches, and identifying trends.
        
        Based on the conversation history and the query, determine which agent should respond next.
        If the query involves multiple areas of expertise, you can specify multiple agents in the order they should respond.
        If the initial query is broad or complex, start with the agent that can best provide foundational information.
        
        Current conversation: {{$conversation}}
        
        Respond with ONLY the name of the next agent (or agents separated by commas if multiple agents should respond in sequence).
        """

        return KernelFunctionFromPrompt(
            function_name="agent_selector",
            description="Selects which agent should respond next based on the query and conversation context",
            prompt=prompt,
        )
        
    async def get_next_agent(self, context):
        """
        Determine which agent should respond next based on the conversation.

        Args:
            context: The chat context containing the message history

        Returns:
            The next agent to respond
        """
        # On first message, analyze the query to determine which agent should start
        if len(context.messages) <= 1:  # Only user message exists
            # Format the conversation history for the agent selection function
            conversation_string = f"Initial Query: {context.messages[0].content}"

            # Invoke the agent selection function
            result = await self._agent_selection_function.invoke(
                variables={"conversation": conversation_string}
            )
            agent_names = [name.strip() for name in result.value.split(",")]

            # Set the initial agent based on the selection
            self._next_agent_index = 0
            self._agent_sequence = [
                self._agents_by_name[name]
                for name in agent_names
                if name in self._agents_by_name
            ]

            # If no valid agents were selected, default to sequential order
            if not self._agent_sequence:
                self._agent_sequence = list(context.agents)

        # Get the next agent from the sequence
        if hasattr(self, "_agent_sequence") and hasattr(self, "_next_agent_index"):
            agent = self._agent_sequence[self._next_agent_index]
            self._next_agent_index = (self._next_agent_index + 1) % len(
                self._agent_sequence
            )
            return agent

        # If something went wrong with the custom selection, default to first agent
        return list(context.agents)[0]


# Create a vertical multi-agent system with the lead agent selection strategy
def create_vertical_agent_system(agents, max_iterations=10):
    """
    Create a vertical multi-agent system where a lead agent forwards requests to specialized agents.

    Args:
        agents: List of specialized agents
        max_iterations: Maximum number of iterations for the conversation

    Returns:
        An AgentGroupChat instance with the vertical architecture
    """
    return AgentGroupChat(
        agents=agents,
        selection_strategy=LeadAgentSelectionStrategy(agents),
        termination_strategy=DefaultTerminationStrategy(
            maximum_iterations=max_iterations
        ),
    )


# Create both collaboration types for comparison
sequential_group = create_sequential_group(
    agents, max_iterations=6
)  # 2 rounds of all 3 agents
vertical_group = create_vertical_agent_system(
    agents, max_iterations=6
)  # Dynamic agent selection

# Test query for vertical collaboration
complex_query = "Given the current inspection data on our bridges and the expected severe weather patterns for next winter, what maintenance priorities should we establish for our water management infrastructure?"


async def main():
    print(
        "\n=== TESTING VERTICAL AGENT COLLABORATION (LEAD AGENT FORWARDS TO SPECIALISTS) ===\n"
    )
    vertical_chat_history = await run_group_chat(vertical_group, complex_query)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
