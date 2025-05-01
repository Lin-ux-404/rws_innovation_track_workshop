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
    conn_string = f"{connection_string.rstrip(';')};Driver=ODBC Driver 17 for SQL Server"
    
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
                            row_dict[columns[i]] = value
                        results.append(row_dict)
        return results
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        raise

@app.route(route="sql/sales/regions", auth_level=func.AuthLevel.ANONYMOUS)
def get_sales_by_region(req: func.HttpRequest) -> func.HttpResponse:
    """Get sales data by region"""
    logging.info("Processing request to get sales data by region.")
    
    try:
        body = req.get_body().decode()
        body_json = json.loads(body)
        region = body_json.get("region_name")
        
        if region:
            query = """
            SELECT 
                r.RegionName,
                CAST(SUM(s.TotalAmount) AS FLOAT) AS TotalSales,
                COUNT(DISTINCT s.SalesID) AS NumberOfTransactions,
                SUM(s.UnitsSold) AS TotalUnitsSold
            FROM 
                SalesData s
                JOIN Customers c ON s.CustomerID = c.CustomerID
                JOIN SalesRegions r ON c.RegionID = r.RegionID
            WHERE 
                r.RegionName = ?
            GROUP BY 
                r.RegionName
            """
            params = [region]
        else:
            query = """
            SELECT 
                r.RegionName,
                CAST(SUM(s.TotalAmount) AS FLOAT) AS TotalSales,
                COUNT(DISTINCT s.SalesID) AS NumberOfTransactions,
                SUM(s.UnitsSold) AS TotalUnitsSold
            FROM 
                SalesData s
                JOIN Customers c ON s.CustomerID = c.CustomerID
                JOIN SalesRegions r ON c.RegionID = r.RegionID
            GROUP BY 
                r.RegionName
            ORDER BY 
                TotalSales DESC
            """
            params = []

        results = run_query(query, params)
        return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error getting sales by region: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error getting sales by region", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )

# Function to get sales data by product category
@app.route(route="sql/sales/by-category", auth_level=func.AuthLevel.ANONYMOUS)
def get_sales_by_category(req: func.HttpRequest) -> func.HttpResponse:
    query = """
    SELECT 
        p.ProductCategory,
        COUNT(DISTINCT s.SalesID) as TotalOrders,
        SUM(s.UnitsSold) as TotalUnitsSold,
        CAST(SUM(s.TotalAmount) AS FLOAT) as TotalRevenue
    FROM 
        SalesData s
        JOIN Products p ON s.ProductID = p.ProductID
    GROUP BY 
        p.ProductCategory
    ORDER BY 
        TotalRevenue DESC
    """
    results = run_query(query)
    return func.HttpResponse(
        json.dumps({"results": results}), mimetype="application/json"
    )

# Function to get sales data by customer segment
@app.route(route="sql/sales/by-channel", auth_level=func.AuthLevel.ANONYMOUS)
def get_sales_by_channel(req: func.HttpRequest) -> func.HttpResponse:
    query = """
    SELECT 
        s.SalesChannel,
        COUNT(DISTINCT s.SalesID) as TotalOrders,
        SUM(s.UnitsSold) as TotalUnitsSold,
        CAST(SUM(s.TotalAmount) AS FLOAT) as TotalRevenue
    FROM 
        SalesData s
    GROUP BY 
        s.SalesChannel
    ORDER BY 
        TotalRevenue DESC
    """
    results = run_query(query)
    return func.HttpResponse(
        json.dumps({"results": results}), mimetype="application/json"
    )

# Function to get top customers based on sales
@app.route(route="sql/customers/top", auth_level=func.AuthLevel.ANONYMOUS)
def get_top_customers(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_body().decode()
        body_json = json.loads(body)
        limit = body_json.get("limit", 10)  # Default to top 10

        query = """
        SELECT 
            c.CustomerName,
            c.CustomerType,
            r.RegionName,
            c.Country,
            COUNT(DISTINCT s.SalesID) as TotalOrders,
            CAST(SUM(s.TotalAmount) AS FLOAT) as TotalSpent
        FROM 
            Customers c
            JOIN SalesData s ON c.CustomerID = s.CustomerID
            JOIN SalesRegions r ON c.RegionID = r.RegionID
        GROUP BY 
            c.CustomerName, c.CustomerType, r.RegionName, c.Country
        ORDER BY 
            TotalSpent DESC
        OFFSET 0 ROWS
        FETCH NEXT ? ROWS ONLY
        """
        results = run_query(query, [limit])
        return func.HttpResponse(
            json.dumps({"results": results}), mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": "Error getting top customers", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )

# Function to get performance metrics for products
@app.route(route="sql/products/performance", auth_level=func.AuthLevel.ANONYMOUS)
def get_product_performance(req: func.HttpRequest) -> func.HttpResponse:
    query = """
    SELECT 
        p.ProductName,
        p.ProductCategory,
        p.ProductLine,
        COUNT(DISTINCT s.SalesID) as TotalOrders,
        SUM(s.UnitsSold) as TotalUnitsSold,
        CAST(SUM(s.TotalAmount) AS FLOAT) as TotalRevenue,
        CAST(AVG(s.TotalAmount) AS FLOAT) as AverageOrderValue
    FROM 
        Products p
        JOIN SalesData s ON p.ProductID = s.ProductID
    GROUP BY 
        p.ProductName, p.ProductCategory, p.ProductLine
    ORDER BY 
        TotalRevenue DESC
    """
    results = run_query(query)
    return func.HttpResponse(json.dumps({"results": results}), mimetype="application/json")