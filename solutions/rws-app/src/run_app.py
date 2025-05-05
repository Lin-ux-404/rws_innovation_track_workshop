import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelFunction

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

# Load environment variables
load_dotenv()

# Initialize the kernel with Azure OpenAI service
kernel = create_kernel_with_service(service_id="azure_chat_completion", temperature=0.7)

# Register plugins
kernel.import_plugin_from_object(ApiManagementPlugin(), plugin_name="ApiPlugin")

# Register RAG plugin if environment variables are set
try:
    kernel.import_plugin_from_object(RAGPlugin(), plugin_name="RAGPlugin")
    rag_enabled = True
    print("RAG Plugin registered successfully")
except ValueError as e:
    print(f"RAG Plugin could not be registered: {e}")
    print("Knowledge-based agents will not be available")
    rag_enabled = False

# Create agents
service_id = "azure_chat_completion"
settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)

data_analyst = create_infrastructure_analyst_agent(kernel, settings)
environmental_expert = create_water_management_expert_agent(kernel, settings)
business_advisor = create_strategic_advisor_agent(kernel, settings)

# Create knowledge-based agents if RAG is enabled
if rag_enabled:
    knowledge_agent = create_knowledge_agent(kernel, settings)
    research_synthesis_agent = create_research_synthesis_agent(kernel, settings)
    print("Knowledge-based agents created")
else:
    knowledge_agent = None
    research_synthesis_agent = None
    print("Knowledge-based agents not available")

def analyze_infrastructure(query=None):
    """Use the Infrastructure Analyst agent to analyze infrastructure assets and safety conditions."""
    if query is None:
        query = "Can you analyze the critical infrastructure assets in Noord-Nederland and recommend prioritization for maintenance based on safety ratings and inspection findings?"
    
    return data_analyst.invoke(query)

def get_water_management_insights(query=None):
    """Use the Water Management Expert agent to analyze water infrastructure and safety conditions."""
    if query is None:
        query = "Looking at safety inspection data for water-related infrastructure in coastal regions, what trends do you notice about maintenance needs?"
    
    return environmental_expert.invoke(query)

def get_strategic_recommendations(query=None):
    """Use the Strategic Advisor agent to get infrastructure management recommendations."""
    if query is None:
        query = "Using the asset statistics and safety inspection data, what strategic recommendations would you make for long-term infrastructure investment?"
    
    return business_advisor.invoke(query)

def search_knowledge_base(query=None):
    """Use the Knowledge Agent to search the knowledge base."""
    if not rag_enabled or knowledge_agent is None:
        return "Knowledge base search is not available. RAG plugin not initialized."
    
    if query is None:
        query = "What are the best practices for maintaining porous asphalt roads?"
    
    return knowledge_agent.invoke(query)

def upload_document_to_knowledge_base(content, title, source="internal", document_type="document"):
    """Upload a document to the knowledge base."""
    if not rag_enabled:
        return "Document upload is not available. RAG plugin not initialized."
    
    rag_functions = kernel.plugins["RAGPlugin"]
    upload_function = rag_functions["upload_document"]
    
    result = upload_function(
        content=content,
        title=title,
        source=source,
        document_type=document_type
    )
    
    return result

def research_with_synthesis(query=None):
    """Use the Research Synthesis Agent to combine knowledge retrieval with data analysis."""
    if not rag_enabled or research_synthesis_agent is None:
        return "Research synthesis is not available. RAG plugin not initialized."
    
    if query is None:
        query = "What innovative maintenance techniques could improve the longevity of our infrastructure assets based on current research?"
    
    return research_synthesis_agent.invoke(query)

def demo_upload_sample_documents():
    """Upload sample documents to demonstrate the RAG capabilities."""
    if not rag_enabled:
        return "Document upload is not available. RAG plugin not initialized."
    
    # Sample document 1: Life-prolonging maintenance techniques
    maintenance_techniques_content = """
    # Life-prolonging Preventive Maintenance Techniques for Porous Asphalt
    
    This document outlines best practices and techniques for maintaining porous asphalt roads to extend their service life
    and optimize performance under various conditions.
    
    ## Key Maintenance Techniques
    
    1. **Regular Cleaning**: Preventive cleaning to maintain porosity and drainage
    2. **Surface Monitoring**: Early detection of wear patterns and potential issues
    3. **Timely Interventions**: Strategic timing of maintenance activities
    4. **Quality Control**: Maintaining consistent standards across maintenance work
    
    ## Implementation Guidelines
    
    - Monitor surface condition regularly, especially after extreme weather
    - Document all maintenance activities and outcomes
    - Use appropriate cleaning methods to preserve surface integrity
    - Implement preventive measures before major issues develop
    """
    
    # Sample document 2: Cold Weather Guidelines
    cold_weather_content = """
    # Asphalt Paving at Temperatures Below Freezing
    
    Technical guidelines from the Dutch Highways Authority for managing asphalt paving operations
    in cold weather conditions to ensure quality and durability.
    
    ## Critical Considerations
    
    1. Material Properties at Low Temperatures
    2. Modified Mixing and Compaction Methods
    3. Weather Monitoring Requirements
    4. Quality Control Measures
    
    ## Special Procedures
    
    - Enhanced temperature monitoring protocols
    - Adjustments to mix designs
    - Modified compaction techniques
    - Additional quality control measures
    """
    
    # Sample document 3: Road Innovation Report
    road_innovation_content = """
    # Innovation Projects in Road Maintenance
    
    Overview of innovative approaches and technologies being implemented in Dutch road maintenance
    operations to improve efficiency and effectiveness.
    
    ## Key Innovation Areas
    
    1. Smart monitoring systems for real-time condition assessment
    2. Advanced materials for longer-lasting repairs
    3. Automated inspection technologies
    4. Sustainable maintenance practices
    
    ## Implementation Strategy
    
    - Pilot testing of new technologies
    - Data-driven decision making
    - Integration with existing systems
    - Cost-benefit analysis framework
    """
    
    # Upload the documents
    result1 = upload_document_to_knowledge_base(
        content=maintenance_techniques_content,
        title="Life-prolonging Preventive Maintenance Techniques for Porous Asphalt",
        source="rijkswaterstaat",
        document_type="technical_guide"
    )
    
    result2 = upload_document_to_knowledge_base(
        content=cold_weather_content,
        title="Asphalt Paving at Temperatures Below Freezing",
        source="rijkswaterstaat",
        document_type="technical_guide"
    )
    
    result3 = upload_document_to_knowledge_base(
        content=road_innovation_content,
        title="Innovation Projects in Road Maintenance",
        source="rijkswaterstaat",
        document_type="research_report"
    )
    
    return f"Sample documents uploaded:\n{result1}\n{result2}\n{result3}"

# Example usage
if __name__ == "__main__":
    # Demonstrate the agents
    
    print("\n=== Infrastructure Analysis ===")
    print(analyze_infrastructure())
    
    print("\n=== Water Management Insights ===")
    print(get_water_management_insights())
    
    print("\n=== Strategic Recommendations ===")
    print(get_strategic_recommendations())
    
    # Demonstrate RAG capabilities if available
    if rag_enabled:
        print("\n=== Uploading Sample Documents ===")
        print(demo_upload_sample_documents())
        
        print("\n=== Knowledge Base Search ===")
        print(search_knowledge_base("What are the best practices for maintaining porous asphalt roads?"))
        
        print("\n=== Research Synthesis ===")
        print(research_with_synthesis("What innovative techniques could improve road maintenance efficiency in cold weather conditions?"))
