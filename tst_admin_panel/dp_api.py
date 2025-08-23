import frappe
import pyodbc
import hashlib
import json
from datetime import date, datetime

CONN_PARAMS = {
    "driver": "FreeTDS",
    "server": "213.186.164.147",
    "port": 1433,
    "database": "TMS",
    "uid": "iadmin",
    "pwd": "ipass",
    "tds_version": "7.3"
}


def get_cache_key(function_name, filters):
    """
    Generate a unique cache key based on the function name and filters.

    Args:
        function_name (str): Name of the function being cached.
        filters (dict): Filters used for the query.

    Returns:
        str: A unique cache key.
    """
    # Serialize the filters dictionary into a sorted JSON string
    filters_string = json.dumps(filters, sort_keys=True)
    # Generate an MD5 hash of the string to ensure a unique key
    hashed_filters = hashlib.md5(filters_string.encode()).hexdigest()
    # Combine the function name and hashed filters into the cache key
    return f"{function_name}:{hashed_filters}"


def get_connection_string(params):
    """
    Build the connection string for the database.
    """
    return (
        f"DRIVER={{{params['driver']}}};"
        f"SERVER={params['server']};"
        f"PORT={params['port']};"
        f"DATABASE={params['database']};"
        f"UID={params['uid']};"
        f"PWD={params['pwd']};"
        f"TDS_Version={params['tds_version']};"
    )


def execute_stored_procedure(procedure_name, params):
    """
    Execute a stored procedure and return all rows.

    Args:
        procedure_name (str): Name of the stored procedure to execute.
        params (tuple): Parameters to pass to the stored procedure.

    Returns:
        list: List of rows returned by the query.
        list: List of column names for the query.
    """
    conn_str = get_connection_string(CONN_PARAMS)
    
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute(f"EXEC {procedure_name} {', '.join(['?' for _ in params])}", params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        conn.close()
        return rows, columns
    except pyodbc.DatabaseError as db_err:
        frappe.log_error(str(db_err), f"{procedure_name} DB Error")
        raise RuntimeError(f"Database error occurred during {procedure_name}: {db_err}")
    except Exception as e:
        frappe.log_error(str(e), f"{procedure_name} Error")
        raise RuntimeError(f"An error occurred during {procedure_name}: {e}")


def format_response(rows, columns):
    """
    Format the rows and columns into a list of dictionaries.
    Converts date or datetime objects to ISO 8601 strings.

    Args:
        rows (list): List of rows from the database.
        columns (list): List of column names.

    Returns:
        list: Formatted list of dictionaries with column names as keys.
    """
    formatted_data = []
    for row in rows:
        formatted_row = {}
        for col_name, value in zip(columns, row):
            if isinstance(value, (date, datetime)):  # Convert date and datetime objects
                formatted_row[col_name] = value.isoformat()
            else:
                formatted_row[col_name] = value
        formatted_data.append(formatted_row)
    return formatted_data


def get_data_with_cache(function_name, procedure_name, filters):
    """
    Retrieve data from cache or database.

    Args:
        function_name (str): Name of the function being called.
        procedure_name (str): Name of the stored procedure to execute.
        filters (dict): Filters used for the query.

    Returns:
        dict: A dictionary containing the query results.
    """
    cache_key = get_cache_key(function_name, filters)
    cache = frappe.cache()

    # Check if data exists in the cache
    cached_data = cache.get_value(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # If not cached, fetch from database
    rows, columns = execute_stored_procedure(procedure_name, tuple(filters.values()))
    result = format_response(rows, columns)

    # Cache the result for 1 day (86400 seconds)
    cache.set_value(cache_key, json.dumps(result), expires_in_sec=86400)

    return result


@frappe.whitelist(allow_guest=True)
def get_car_fuel_report(customerID, fromdate, todate):
    """
    Retrieve car fuel report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_car_fuel_report", "dbo.uspGetCarFuelReport", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }

@frappe.whitelist(allow_guest=True)
def get_car_sum_fuel_report(customerID, fromdate, todate):
    """
    Retrieve car fuel report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_car_sum_fuel_report", "dbo.uspGetCarSUMFuelReport", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }


@frappe.whitelist(allow_guest=True)
def get_car_consum_report(customerID, fromdate, todate):
    """
    Retrieve car consumption report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_car_consum_report", "dbo.uspGetccarconsumReport", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }

@frappe.whitelist(allow_guest=True)
def get_kpi(customerID, fromdate, todate):
    """
    Retrieve KPI report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_kpi", "dbo.uspGetKPIReport", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }

@frappe.whitelist(allow_guest=True)
def get_Fuel_Distribution(customerID, fromdate, todate):
    """
    Retrieve fuel distribution report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_Fuel_Distribution", "dbo.uspGetFuelDistribution", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }

@frappe.whitelist(allow_guest=True)
def get_Top10_Car_Fuel_Report(customerID, fromdate, todate):
    """
    Retrieve top 10 car fuel report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_Top10_Car_Fuel_Report", "dbo.uspGetTop10CarFuelReport", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }

@frappe.whitelist(allow_guest=True)
def get_Fuel_Distribution_Line(customerID, fromdate, todate):
    """
    Retrieve fuel distribution line report for a given customer and date range.
    """
    try:
        filters = {"customerID": customerID, "fromdate": fromdate, "todate": todate}
        result = get_data_with_cache("get_Fuel_Distribution_Line", "dbo.uspGetFuelDistributionLine", filters)
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": len(result)
        }
    except RuntimeError as e:
        frappe.local.response["http_status_code"] = 500
        return {
            "status": 0,
            "message": str(e),
            "data": [],
            "total": 0
        }