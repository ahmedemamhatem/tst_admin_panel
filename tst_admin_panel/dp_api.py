
import frappe
import pyodbc

CONN_PARAMS = {
    "driver": "FreeTDS",
    "server": "213.186.164.147",
    "port": 1433,
    "database": "TMS",
    "uid": "iadmin",
    "pwd": "ipass",
    "tds_version": "7.3"
}

def get_connection_string(params):
    return (
        f"DRIVER={{{params['driver']}}};"
        f"SERVER={params['server']};"
        f"PORT={params['port']};"
        f"DATABASE={params['database']};"
        f"UID={params['uid']};"
        f"PWD={params['pwd']};"
        f"TDS_Version={params['tds_version']};"
    )

@frappe.whitelist(allow_guest=True)
def get_car_fuel_report(customerID, fromdate, todate, page=1, take=None, offset=None, limit=None):
    """
    Retrieve paginated car fuel report for a given customer and date range.

    Args:
        customerID (str): Customer ID to filter results.
        fromdate (str): Start date for the report.
        todate (str): End date for the report.
        page (int, optional): Page number for pagination. Defaults to 1.
        take (int, optional): Number of records per page (priority over limit). Defaults to None.
        offset (int, optional): Record offset for pagination. Defaults to calculated from page and page_size.
        limit (int, optional): Number of records per page if 'take' not provided. Defaults to None.

    Returns:
        dict: A dictionary containing status, message, data list, total record count, current page, and page size.
    """
    frappe.local.response["Access-Control-Allow-Origin"] = "*"
    frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type"

    try:
        page = int(page) if page else 1
        page_size = int(take or limit or 20)
        offset = int(offset) if offset is not None else (page - 1) * page_size
    except Exception:
        frappe.local.response["http_status_code"] = 400
        return {
            "status": 0,
            "message": "Invalid pagination parameters",
            "data": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        }

    result = []
    total_count = 0
    conn_str = get_connection_string(CONN_PARAMS)

    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "EXEC dbo.uspGetCarFuelReport @customerID=?, @fromdate=?, @todate=?",
            (customerID, fromdate, todate)
        )
        all_rows = cursor.fetchall()
        total_count = len(all_rows)
        paginated_rows = all_rows[offset:offset + page_size] if total_count else []
        columns = [column[0] for column in cursor.description]
        for row in paginated_rows:
            result.append(dict(zip(columns, row)))
        cursor.close()
        conn.close()

        frappe.local.response["http_status_code"] = 200
        return {
            "status": 1,
            "data": result,
            "message": "Success",
            "total": total_count,
            "page": page,
            "page_size": page_size
        }

    except pyodbc.DatabaseError as db_err:
        frappe.local.response["http_status_code"] = 500
        frappe.log_error(str(db_err), "Car Fuel Report DB Error")
        return {
            "status": 0,
            "message": "Database error occurred.",
            "data": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "error_detail": str(db_err)
        }
    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        frappe.log_error(str(e), "Car Fuel Report Error")
        return {
            "status": 0,
            "message": "Internal server error",
            "data": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "error_detail": str(e)
        }
