import logging
import azure.functions as func
import pyodbc
import json
import os
import re
from decimal import Decimal

# Configure the function app
app = func.FunctionApp()

def format_connection_string(connection_string: str) -> str:
    """
    Format and standardize SQL Server connection string.
    
    Args:
        connection_string: The original connection string
        
    Returns:
        Formatted connection string with standardized parameters
    """
    if not connection_string:
        raise ValueError("Connection string cannot be empty")

    # Add ODBC Driver
    conn_string = f"{connection_string.rstrip(';')};Driver=ODBC Driver 18 for SQL Server"
    
    # Standardize parameter names and values
    replacements = [
        (r"Encrypt=True|Encrypt=False", 
         lambda m: "Encrypt=yes" if m.group() == "Encrypt=True" else "Encrypt=no"),
        (r"TrustServerCertificate=True|TrustServerCertificate=False",
         lambda m: "TrustServerCertificate=yes" if m.group() == "TrustServerCertificate=True" else "TrustServerCertificate=no"),
        (r"User ID=", "UID="),
        (r"Password=", "PWD="),
        (r"Initial Catalog=", "Database=")
    ]
    
    # Apply all replacements
    for pattern, replacement in replacements:
        if callable(replacement):
            conn_string = re.sub(pattern, replacement, conn_string)
        else:
            conn_string = re.sub(pattern, replacement, conn_string)
    
    return conn_string

# Get and format connection string from environment variables
SQL_CONNECTION_STRING = os.environ.get("SQL_CONNECTION_STRING")
if SQL_CONNECTION_STRING:
    conn_string = format_connection_string(SQL_CONNECTION_STRING)
else:
    raise ValueError("SQL_CONNECTION_STRING environment variable is not set")

def run_query(query: str, params=None):
    """Execute a SQL query and return the results"""
    from datetime import datetime, date
    results = []
    
    try:
        with pyodbc.connect(conn_string, timeout=30) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                if cursor.description:
                    columns = [c[0] for c in cursor.description]
                    for row in cursor.fetchall():
                        # Convert row to dict
                        row_dict = {}
                        for i, value in enumerate(row):
                            # Convert Decimal to float for JSON serialization
                            if isinstance(value, Decimal):
                                value = float(value)
                            # Convert date/datetime to string for JSON serialization
                            elif isinstance(value, datetime):
                                value = value.strftime('%Y-%m-%d %H:%M:%S')
                            elif isinstance(value, date):
                                value = value.strftime('%Y-%m-%d')
                            row_dict[columns[i]] = value
                        results.append(row_dict)
        return results
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        raise

@app.route(route="sql/infrastructure/critical", auth_level=func.AuthLevel.ANONYMOUS)
def get_critical_assets(req: func.HttpRequest) -> func.HttpResponse:
    """Get critical infrastructure assets that need immediate attention"""
    logging.info("Processing request to get critical infrastructure assets")
    
    try:
        query = """
        SELECT * FROM vw_CriticalAssets
        ORDER BY SafetyRating ASC, InspectionDate DESC
        """
        results = run_query(query)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting critical assets: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting critical assets", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="sql/infrastructure/by-region", auth_level=func.AuthLevel.ANONYMOUS)
def get_assets_by_region(req: func.HttpRequest) -> func.HttpResponse:
    """Get infrastructure assets by region with their current status"""
    try:
        body = req.get_body().decode()
        body_json = json.loads(body)
        region = body_json.get("region_name")
        
        if region:
            query = """
            SELECT 
                r.RegionName,
                a.AssetType,
                a.AssetName,
                a.Status,
                a.ConstructionYear,
                a.LastMajorMaintenance,
                i.SafetyRating,
                i.InspectionDate
            FROM 
                InfrastructureAssets a
                JOIN Regions r ON a.RegionID = r.RegionID
                LEFT JOIN (
                    SELECT AssetID, SafetyRating, InspectionDate,
                           ROW_NUMBER() OVER (PARTITION BY AssetID ORDER BY InspectionDate DESC) as rn
                    FROM SafetyInspections
                ) i ON a.AssetID = i.AssetID AND i.rn = 1
            WHERE 
                r.RegionName = ?
            ORDER BY 
                a.Status DESC, i.SafetyRating ASC
            """
            params = [region]
        else:
            query = """
            SELECT 
                r.RegionName,
                COUNT(a.AssetID) as TotalAssets,
                SUM(CASE WHEN a.Status = 'Critical' THEN 1 ELSE 0 END) as CriticalAssets,
                SUM(CASE WHEN a.Status = 'Under Maintenance' THEN 1 ELSE 0 END) as UnderMaintenance,
                AVG(CAST(i.SafetyRating as FLOAT)) as AvgSafetyRating
            FROM 
                InfrastructureAssets a
                JOIN Regions r ON a.RegionID = r.RegionID
                LEFT JOIN (
                    SELECT AssetID, SafetyRating,
                           ROW_NUMBER() OVER (PARTITION BY AssetID ORDER BY InspectionDate DESC) as rn
                    FROM SafetyInspections
                ) i ON a.AssetID = i.AssetID AND i.rn = 1
            GROUP BY 
                r.RegionName
            ORDER BY 
                CriticalAssets DESC, AvgSafetyRating ASC
            """
            params = []

        results = run_query(query, params)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting assets by region: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting assets by region", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="sql/maintenance/active-projects", auth_level=func.AuthLevel.ANONYMOUS)
def get_active_projects(req: func.HttpRequest) -> func.HttpResponse:
    """Get active maintenance projects"""
    try:
        query = """
        SELECT * FROM vw_ActiveProjects
        ORDER BY Priority DESC, StartDate ASC
        """
        results = run_query(query)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting active projects: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting active projects", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="sql/safety/inspections", auth_level=func.AuthLevel.ANONYMOUS)
def get_safety_inspections(req: func.HttpRequest) -> func.HttpResponse:
    """Get safety inspection reports"""
    try:
        body = req.get_body().decode()
        body_json = json.loads(body)
        asset_type = body_json.get("asset_type")
        min_safety_rating = body_json.get("min_safety_rating", 1)
        max_safety_rating = body_json.get("max_safety_rating", 5)
        
        query = """
        SELECT 
            i.InspectionID,
            a.AssetName,
            a.AssetType,
            r.RegionName,
            i.InspectionDate,
            i.InspectionType,
            i.SafetyRating,
            i.Findings,
            i.RecommendedActions
        FROM 
            SafetyInspections i
            JOIN InfrastructureAssets a ON i.AssetID = a.AssetID
            JOIN Regions r ON a.RegionID = r.RegionID
        WHERE 
            i.SafetyRating BETWEEN ? AND ?
            AND (? IS NULL OR a.AssetType = ?)
        ORDER BY 
            i.InspectionDate DESC, i.SafetyRating ASC
        """
        
        params = [min_safety_rating, max_safety_rating, asset_type]
        if asset_type:
            params.append(asset_type)
        else:
            params.append(None)

        results = run_query(query, params)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting safety inspections: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting safety inspections", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="sql/assets/statistics", auth_level=func.AuthLevel.ANONYMOUS)
def get_asset_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """Get statistical overview of infrastructure assets"""
    try:
        query = """
        SELECT 
            AssetType,
            COUNT(*) as TotalAssets,
            AVG(YEAR(GETDATE()) - ConstructionYear) as AvgAge,
            SUM(CASE WHEN Status = 'Critical' THEN 1 ELSE 0 END) as CriticalCount,
            SUM(CASE WHEN Status = 'Under Maintenance' THEN 1 ELSE 0 END) as UnderMaintenanceCount,
            SUM(CASE WHEN Status = 'Operational' THEN 1 ELSE 0 END) as OperationalCount
        FROM 
            InfrastructureAssets
        GROUP BY 
            AssetType
        ORDER BY 
            TotalAssets DESC
        """
        results = run_query(query)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting asset statistics: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting asset statistics", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
