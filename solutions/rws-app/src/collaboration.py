import asyncio
from typing import List
from semantic_kernel.contents import ChatHistory, ChatMessageContent
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import SequentialSelectionStrategy, DefaultTerminationStrategy
from semantic_kernel.agents.strategies.selection.selection_strategy import SelectionStrategy

async def test_agent(agent, user_message):
    """Test an individual agent with a user message.
    
    Args:
        agent: The ChatCompletionAgent to test
        user_message: The message to send to the agent
    """
    print(f"\n=== Testing {agent.name} ===\n")
    print(f"User: {user_message}\n")
    
    # Create a chat history
    chat_history = ChatHistory()
    chat_history.add_user_message(user_message)
    
    # Get response from the agent
    response = await agent.get_response(messages=chat_history)
    
    print(f"{agent.name}: {response.content}\n")
    print("=== Test Complete ===\n")
    
    return response

def create_sequential_group(agents, max_iterations=6):
    """Create a sequential (round-robin) agent group chat.
    
    Args:
        agents: List of agent instances
        max_iterations: Maximum number of iterations
    """
    return AgentGroupChat(
        agents=agents,
        selection_strategy=SequentialSelectionStrategy(),
        termination_strategy=DefaultTerminationStrategy(maximum_iterations=max_iterations),
    )

def create_fixed_workflow_chat(agents, workflow_sequence, max_iterations=None):
    """Create a chat with a fixed agent workflow sequence.
    
    Args:
        agents: List of agent instances
        workflow_sequence: List of agent names in the desired workflow order
        max_iterations: Maximum number of iterations (default: len(workflow_sequence))
    """
    # Create a mapping of agent names to instances
    agent_map = {agent.name: agent for agent in agents}
    
    # Verify all workflow agents exist
    for name in workflow_sequence:
        if name not in agent_map:
            raise ValueError(f"Agent '{name}' in workflow not found in provided agents")
    
    # Create a custom selection strategy class
    class FixedWorkflowStrategy(SelectionStrategy):
        def __init__(self, workflow_sequence):
            super().__init__()
            self.workflow_sequence = workflow_sequence
            self.counter = 0
            self.has_selected = False
        
        async def next(self, agents, messages):
            agent = agent_map[
                self.workflow_sequence[self.counter % len(self.workflow_sequence)]
            ]
            self.counter += 1
            print(f"Selected: {agent.name}")
            
            self.has_selected = True
            return agent
    
    # Set maximum iterations if not specified
    if max_iterations is None:
        max_iterations = len(workflow_sequence)
    
    fixed_workflow_strategy = FixedWorkflowStrategy(workflow_sequence=workflow_sequence)
    
    # Create and return the AgentGroupChat
    return AgentGroupChat(
        agents=agents,
        selection_strategy=fixed_workflow_strategy,
        termination_strategy=DefaultTerminationStrategy(
            maximum_iterations=max_iterations
        ),
    )

async def run_group_chat(chat, user_message):
    """Run a multi-agent conversation and display the results.
    
    Args:
        chat: The AgentGroupChat instance
        user_message: The initial user message to start the conversation
    
    Returns:
        The chat history containing all messages
    """
    # Create a new chat history if needed
    if not hasattr(chat, "history") or chat.history is None:
        chat_history = ChatHistory()
        chat.history = chat_history
    
    # Add the user message to the chat
    await chat.add_chat_message(message=user_message)
    print(f"\nUser: {user_message}\n")
    print("=== Beginning Agent Collaboration ===\n")
    
    # Track which agent is speaking for formatting
    current_agent = None
    
    # Invoke the chat and process agent responses
    try:
        async for response in chat.invoke():
            if response is not None and response.name:
                # Add a separator between different agents
                if current_agent != response.name:
                    current_agent = response.name
                    print(f"\n## {response.name}:\n{response.content}")
                else:
                    # Same agent continuing
                    print(f"{response.content}")
        
        print("\n=== Agent Collaboration Complete ===\n")
    except Exception as e:
        print(f"Error during chat invocation: {str(e)}")
    
    # Reset is_complete to allow for further conversations
    chat.is_complete = False
    
    return chat.history
