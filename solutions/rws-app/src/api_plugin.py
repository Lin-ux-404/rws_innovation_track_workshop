import os
import json
import requests
from typing import Annotated
from semantic_kernel.functions import kernel_function

class ApiManagementPlugin:
    """A plugin for connecting to services through Azure API Management."""
    
    def __init__(self):
        self.apim_url = os.getenv("APIM_GATEWAY_URL")
        self.subscription_key = os.getenv("APIM_SUBSCRIPTION_KEY")
        
        if not self.apim_url or not self.subscription_key:
            raise ValueError("APIM_GATEWAY_URL and APIM_SUBSCRIPTION_KEY environment variables must be set")
    
    def _call_api(self, endpoint: str, payload: dict) -> dict:
        """Helper method to call API endpoints through APIM.
        
        Args:
            endpoint: The API endpoint path (e.g., '/weather')
            payload: The JSON payload to send
            
        Returns:
            The API response as a dictionary
        """
        url = f"{self.apim_url}{endpoint}"
        headers = {"api-key": self.subscription_key, "Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @kernel_function(description="Get weather information for a location.")
    def get_weather(
        self,
        location: Annotated[str, "The location to get weather for (city name)"],
        unit: Annotated[str, "Temperature unit: 'celsius' or 'fahrenheit'"] = "celsius"
    ) -> str:
        """Get current weather information for a specific location."""
        payload = {"location": location, "unit": unit}
        result = self._call_api("/weather", payload)
        
        if "error" in result:
            return f"Error getting weather: {result['error']}"
        
        return f"The current temperature in {result['location']} is {result['temperature']} degrees {result['unit']}."
    
    @kernel_function(description="Execute a SQL query against the database.")
    def execute_sql_query(
        self,
        query: Annotated[str, "The SQL query to execute"]
    ) -> str:
        """Execute a SQL query against the database and return the results."""
        payload = {"query": query}
        result = self._call_api("/sql", payload)
        
        if "error" in result:
            return f"Error executing SQL query: {result['error']}"
        
        # Format the results nicely
        formatted_results = json.dumps(result["results"], indent=2)
        return f"Query executed in {result.get('executionTime', 'unknown')} seconds. Results:\n{formatted_results}"
    
    @kernel_function(description="Get sales data for a specific region.")
    def get_sales_by_region(
        self,
        region_name: Annotated[str, "Optional name of the region to filter by. If not provided, data for all regions will be returned"] = None
    ) -> str:
        """Get sales data grouped by region or for a specific region."""
        payload = {}
        if region_name:
            payload["region_name"] = region_name
            
        result = self._call_api("/sales/regions", payload)
        
        if "error" in result:
            return f"Error getting sales by region: {result['error']}"
        
        # Format the results nicely
        formatted_results = json.dumps(result["results"], indent=2)
        return f"Sales by region:\n{formatted_results}"
