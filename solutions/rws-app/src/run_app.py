import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelFunction

from kernel_setup import create_kernel_with_service
from api_plugin import ApiManagementPlugin
from rag_plugin import RAGPlugin
from agents import (
    create_data_analyst_agent, 
    create_environmental_expert_agent, 
    create_business_advisor_agent,
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

data_analyst = create_data_analyst_agent(kernel, settings)
environmental_expert = create_environmental_expert_agent(kernel, settings)
business_advisor = create_business_advisor_agent(kernel, settings)

# Create knowledge-based agents if RAG is enabled
if rag_enabled:
    knowledge_agent = create_knowledge_agent(kernel, settings)
    research_synthesis_agent = create_research_synthesis_agent(kernel, settings)
    print("Knowledge-based agents created")
else:
    knowledge_agent = None
    research_synthesis_agent = None
    print("Knowledge-based agents not available")

def analyze_sales_data(query=None):
    """Use the Data Analyst agent to analyze sales data."""
    if query is None:
        query = "What are the top-selling products in each region? Please analyze the data and provide insights."
    
    return data_analyst.invoke(query)

def get_weather_insights(location=None):
    """Use the Environmental Expert agent to get weather insights."""
    if location is None:
        location = "Analyze the weather conditions in Amsterdam and their potential impact on agricultural operations."
    
    return environmental_expert.invoke(location)

def get_business_recommendations(query=None):
    """Use the Business Advisor agent to get business recommendations."""
    if query is None:
        query = "Based on the sales data and weather conditions, what business strategies should we consider for the next quarter?"
    
    return business_advisor.invoke(query)

def search_knowledge_base(query=None):
    """Use the Knowledge Agent to search the knowledge base."""
    if not rag_enabled or knowledge_agent is None:
        return "Knowledge base search is not available. RAG plugin not initialized."
    
    if query is None:
        query = "Find information about crop yield optimization techniques."
    
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
        query = "How do current weather patterns compare to historical trends, and what are the implications for our crop selection strategy?"
    
    return research_synthesis_agent.invoke(query)

def demo_upload_sample_documents():
    """Upload sample documents to demonstrate the RAG capabilities."""
    if not rag_enabled:
        return "Document upload is not available. RAG plugin not initialized."
    
    # Sample document 1: Crop Rotation Guide
    crop_rotation_content = """
    # Crop Rotation Best Practices
    
    Crop rotation is the practice of growing different types of crops in the same area across sequential seasons. 
    It's done to avoid depleting the soil of specific nutrients and to control pests and diseases.
    
    ## Benefits of Crop Rotation
    
    1. **Soil Health**: Different crops have different nutrient needs and contribute different benefits to the soil.
    2. **Pest and Disease Control**: Many pests and diseases are specific to certain plant families.
    3. **Weed Suppression**: Some crops can help suppress specific weeds.
    4. **Improved Yield**: Proper rotation can increase yield by 10-15% compared to continuous cropping.
    
    ## Common Rotation Patterns
    
    - 3-Year Rotation: Leafy greens → Fruit crops → Root vegetables
    - 4-Year Rotation: Legumes → Brassicas → Alliums → Cucurbits
    
    For optimal results, maintain detailed records of crop performance and rotate based on plant families, not just individual crops.
    """
    
    # Sample document 2: Climate Impact Analysis
    climate_impact_content = """
    # Climate Change Impact on Agricultural Productivity
    
    Recent studies indicate significant shifts in growing conditions across Europe due to climate change.
    
    ## Temperature Trends
    
    Average temperatures have increased by 1.2°C over the past 50 years in Northern Europe, with more pronounced warming during winter months.
    
    ## Precipitation Patterns
    
    - Southern Europe: Decreased annual rainfall by 12% since 1980
    - Northern Europe: Increased annual rainfall by 8% since 1980
    - More extreme precipitation events across all regions
    
    ## Impact on Growing Seasons
    
    1. Growing seasons have extended by 10-15 days in Northern regions
    2. Increased heat stress during summer months affects flowering and fruit development
    3. Changed precipitation patterns affect irrigation needs and water management strategies
    
    Adaptation strategies include selecting heat-tolerant varieties, adjusting planting schedules, and implementing water conservation measures.
    """
    
    # Sample document 3: Market Trends Report
    market_trends_content = """
    # Agricultural Market Trends 2024-2025
    
    This report summarizes key market trends affecting agricultural producers in Europe.
    
    ## Consumer Preferences
    
    - 68% increase in demand for organic produce since 2020
    - 42% of consumers willing to pay premium prices for locally-grown produce
    - Rising interest in heritage and heirloom varieties
    
    ## Supply Chain Developments
    
    1. Direct-to-consumer models growing at 23% annually
    2. Increased use of blockchain for traceability and transparency
    3. Consolidation among distributors creating both challenges and opportunities
    
    ## Price Projections
    
    | Crop Category | Price Trend | Key Factors |
    |---------------|-------------|-------------|
    | Vegetables    | +5-8%       | Input costs, labor shortages |
    | Fruits        | +3-6%       | Weather events, transportation |
    | Grains        | +2-4%       | Global supply, biofuel demand |
    
    Producers focusing on specialty crops, sustainable practices, and direct marketing channels are projected to see the strongest revenue growth.
    """
    
    # Upload the documents
    result1 = upload_document_to_knowledge_base(
        content=crop_rotation_content,
        title="Crop Rotation Best Practices Guide",
        source="research",
        document_type="guide"
    )
    
    result2 = upload_document_to_knowledge_base(
        content=climate_impact_content,
        title="Climate Change Impact Analysis 2024",
        source="research",
        document_type="report"
    )
    
    result3 = upload_document_to_knowledge_base(
        content=market_trends_content,
        title="Agricultural Market Trends 2024-2025",
        source="market_analysis",
        document_type="report"
    )
    
    return f"Sample documents uploaded:\n{result1}\n{result2}\n{result3}"

# Example usage
if __name__ == "__main__":
    # Demonstrate the agents
    
    print("\n=== Data Analysis ===")
    print(analyze_sales_data())
    
    print("\n=== Weather Insights ===")
    print(get_weather_insights())
    
    print("\n=== Business Recommendations ===")
    print(get_business_recommendations())
    
    # Demonstrate RAG capabilities if available
    if rag_enabled:
        print("\n=== Uploading Sample Documents ===")
        print(demo_upload_sample_documents())
        
        print("\n=== Knowledge Base Search ===")
        print(search_knowledge_base("What are the benefits of crop rotation?"))
        
        print("\n=== Research Synthesis ===")
        print(research_with_synthesis("How might climate change affect our crop rotation strategies based on the knowledge base?"))
