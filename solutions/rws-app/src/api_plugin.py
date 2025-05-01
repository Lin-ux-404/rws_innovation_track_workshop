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
            raise ValueError(
                "APIM_GATEWAY_URL and APIM_SUBSCRIPTION_KEY environment variables must be set"
            )

    def _call_api(self, endpoint: str, payload: dict) -> dict:
        """Helper method to call API endpoints through APIM.

        Args:
            endpoint: The API endpoint path (e.g., '/infrastructure/critical')
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

    @kernel_function(description="Get information about critical infrastructure assets.")
    def get_critical_assets(self) -> str:
        """Get list of infrastructure assets that require immediate attention."""
        result = self._call_api("/sql/infrastructure/critical", {})
        
        if "error" in result:
            return f"Error getting critical assets: {result['error']}"

        if not result["results"]:
            return "No critical assets found."

        formatted_results = []
        for asset in result["results"]:
            formatted_results.append(
                f"Asset: {asset['AssetName']} ({asset['AssetType']})\n"
                f"Region: {asset['RegionName']}\n"
                f"Status: {asset['Status']}\n"
                f"Safety Rating: {asset['SafetyRating']}/5\n"
                f"Last Inspection: {asset['InspectionDate']}\n"
            )

        return "\nCritical Assets Report:\n\n" + "\n".join(formatted_results)

    @kernel_function(description="Get infrastructure assets by region.")
    def get_assets_by_region(
        self,
        region_name: Annotated[
            str,
            "Optional name of the region to filter by. If not provided, summary for all regions will be returned."
        ] = None,
    ) -> str:
        """Get infrastructure assets information for a specific region."""
        payload = {}
        if region_name:
            payload["region_name"] = region_name

        result = self._call_api("/sql/infrastructure/by-region", payload)

        if "error" in result:
            return f"Error getting assets by region: {result['error']}"

        if not result["results"]:
            return "No assets found for the specified criteria."

        if region_name:
            # Detailed view for specific region
            formatted_results = []
            for asset in result["results"]:
                formatted_results.append(
                    f"Asset: {asset['AssetName']}\n"
                    f"Type: {asset['AssetType']}\n"
                    f"Status: {asset['Status']}\n"
                    f"Construction Year: {asset['ConstructionYear']}\n"
                    f"Last Major Maintenance: {asset['LastMajorMaintenance']}\n"
                    f"Safety Rating: {asset['SafetyRating'] if asset['SafetyRating'] else 'Not Available'}\n"
                    f"Last Inspection: {asset['InspectionDate'] if asset['InspectionDate'] else 'Not Available'}\n"
                )
            return f"\nInfrastructure Assets in {region_name}:\n\n" + "\n".join(formatted_results)
        else:
            # Summary view for all regions
            formatted_results = []
            for region in result["results"]:
                formatted_results.append(
                    f"Region: {region['RegionName']}\n"
                    f"Total Assets: {region['TotalAssets']}\n"
                    f"Critical Assets: {region['CriticalAssets']}\n"
                    f"Under Maintenance: {region['UnderMaintenance']}\n"
                    f"Average Safety Rating: {region['AvgSafetyRating']:.1f}/5\n"
                )
            return "\nRegional Infrastructure Summary:\n\n" + "\n".join(formatted_results)

    @kernel_function(description="Get information about active maintenance projects.")
    def get_active_projects(self) -> str:
        """Get list of ongoing and planned maintenance projects."""
        result = self._call_api("/sql/maintenance/active-projects", {})

        if "error" in result:
            return f"Error getting active projects: {result['error']}"

        if not result["results"]:
            return "No active maintenance projects found."

        formatted_results = []
        for project in result["results"]:
            formatted_results.append(
                f"Project: {project['ProjectName']}\n"
                f"Type: {project['ProjectType']}\n"
                f"Asset: {project['AssetName']} ({project['AssetType']})\n"
                f"Region: {project['RegionName']}\n"
                f"Priority: {project['Priority']}\n"
                f"Status: {project['Status']}\n"
                f"Timeline: {project['StartDate']} to {project['EndDate']}\n"
                f"Budget: €{project['Budget']:,.2f}\n"
            )

        return "\nActive Maintenance Projects:\n\n" + "\n".join(formatted_results)

    @kernel_function(description="Get safety inspection reports for infrastructure assets.")
    def get_safety_inspections(
        self,
        asset_type: Annotated[str, "Type of asset to filter by (e.g., 'Bridge', 'Highway', 'Waterway')"] = None,
        min_safety_rating: Annotated[int, "Minimum safety rating (1-5)"] = 1,
        max_safety_rating: Annotated[int, "Maximum safety rating (1-5)"] = 5,
    ) -> str:
        """Get safety inspection reports filtered by criteria."""
        payload = {
            "asset_type": asset_type,
            "min_safety_rating": min_safety_rating,
            "max_safety_rating": max_safety_rating
        }

        result = self._call_api("/sql/safety/inspections", payload)

        if "error" in result:
            return f"Error getting safety inspections: {result['error']}"

        if not result["results"]:
            return "No safety inspections found matching the criteria."

        formatted_results = []
        for inspection in result["results"]:
            formatted_results.append(
                f"Asset: {inspection['AssetName']} ({inspection['AssetType']})\n"
                f"Region: {inspection['RegionName']}\n"
                f"Inspection Date: {inspection['InspectionDate']}\n"
                f"Type: {inspection['InspectionType']}\n"
                f"Safety Rating: {inspection['SafetyRating']}/5\n"
                f"Findings: {inspection['Findings']}\n"
                f"Recommended Actions: {inspection['RecommendedActions']}\n"
            )

        header = "\nSafety Inspection Reports"
        if asset_type:
            header += f" for {asset_type}s"
        header += f" (Safety Rating: {min_safety_rating}-{max_safety_rating}):\n"

        return header + "\n".join(formatted_results)

    @kernel_function(description="Get statistical overview of infrastructure assets.")
    def get_asset_statistics(self) -> str:
        """Get statistical overview of all infrastructure assets."""
        result = self._call_api("/sql/assets/statistics", {})

        if "error" in result:
            return f"Error getting asset statistics: {result['error']}"

        if not result["results"]:
            return "No asset statistics available."

        formatted_results = []
        for stat in result["results"]:
            formatted_results.append(
                f"Asset Type: {stat['AssetType']}\n"
                f"Total Assets: {stat['TotalAssets']}\n"
                f"Average Age: {stat['AvgAge']:.1f} years\n"
                f"Status Breakdown:\n"
                f"  - Critical: {stat['CriticalCount']}\n"
                f"  - Under Maintenance: {stat['UnderMaintenanceCount']}\n"
                f"  - Operational: {stat['OperationalCount']}\n"
            )

        return "\nInfrastructure Asset Statistics:\n\n" + "\n".join(formatted_results)
