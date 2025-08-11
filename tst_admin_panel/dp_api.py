# sudo apt-get update
# sudo apt-get install -y freetds-dev freetds-bin tdsodbc unixodbc unixodbc-dev python3-pip

# # Install Python ODBC library
# pip3 install pyodbc

# # Add FreeTDS driver to /etc/odbcinst.ini if not already present
# ODBCINST="/etc/odbcinst.ini"
# FREETDS_DRIVER="Driver=/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"
# if ! grep -q "\[FreeTDS\]" "$ODBCINST"; then
#   echo -e "\n[FreeTDS]\nDescription=FreeTDS Driver for MSSQL\n$FREETDS_DRIVER" | sudo tee -a "$ODBCINST"
# else
#   if ! grep -q "$FREETDS_DRIVER" "$ODBCINST"; then
#     sudo sed -i "/\[FreeTDS\]/a $FREETDS_DRIVER" "$ODBCINST"
#   fi
# fi

# echo "-------------------------------------"
# echo "FreeTDS, ODBC, and pyodbc installed!"
# echo "You can now use FreeTDS with pyodbc."
# echo "-------------------------------------"
# # 1. Update System
# sudo apt update
# sudo apt upgrade -y

# # 2. Install unixODBC and tools
# sudo apt install -y unixodbc unixodbc-dev odbcinst curl gpg

# # 3. Add Microsoft GPG key
# curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null

# # 4. Add Microsoft repo for Ubuntu 22.04 (works for 24.04 too)
# echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | sudo tee /etc/apt/sources.list.d/msprod.list

# # 5. Update package lists again
# sudo apt update

# # 6. Install MS ODBC driver
# sudo ACCEPT_EULA=Y apt install -y msodbcsql17

# # 7. Verify driver
# echo "Installed ODBC drivers:"
# odbcinst -q -d

# # 8. Install Python package inside your virtualenv (if any)
# # If you use a virtualenv, activate it first!
# pip install --upgrade pip
# pip install pyodbc

# echo "All done! Your system is ready for Frappe + pyodbc + Microsoft SQL Server."

import frappe
import pyodbc

@frappe.whitelist(allow_guest=True)
def get_car_fuel_report(customerID, fromdate, todate, page=1, take=None, offset=None, limit=None):
    # CORS Headers
    frappe.local.response["Access-Control-Allow-Origin"] = "*"
    frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type"

    # Pagination logic
    try:
        page = int(page) if page else 1
        # Prefer 'take', then 'limit', then default 20
        page_size = int(take or limit or 20)
        offset = int(offset) if offset is not None else (page-1) * page_size
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

    conn_str = (
        "DRIVER={FreeTDS};"
        "SERVER=213.186.164.147;"
        "PORT=1433;"
        "DATABASE=TMS;"
        "UID=iadmin;"
        "PWD=ipass;"
        "TDS_Version=7.3;"
    )

    result = []
    total_count = 0
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()

        # Get total count for pagination
        count_query = """
            SELECT COUNT(*) FROM (
                EXEC dbo.uspGetCarFuelReport @customerID=?, @fromdate=?, @todate=?
            ) AS count_table
        """

        try:
            cursor.execute(
                "EXEC dbo.uspGetCarFuelReport @customerID=?, @fromdate=?, @todate=?",
                (customerID, fromdate, todate)
            )
            all_rows = cursor.fetchall()
            total_count = len(all_rows)
        except Exception as count_ex:
            total_count = 0  # fallback

        # Apply pagination to results
        # Use slicing on all_rows for pagination
        paginated_rows = all_rows[offset:offset+page_size] if total_count else []

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