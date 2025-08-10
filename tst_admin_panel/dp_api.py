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
def get_car_fuel_report(customerID, fromdate, todate):
    frappe.local.response["Access-Control-Allow-Origin"] = "*"
    frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type"

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
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "EXEC dbo.uspGetCarFuelReport @customerID=?, @fromdate=?, @todate=?",
            (customerID, fromdate, todate)
        )
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))
        cursor.close()
        conn.close()
        return {"status": 1, "data": result, "message": "Success"}
    except Exception as e:
        frappe.log_error(str(e), "Car Fuel Report Error")
        return {"status": 0, "data": [], "message": str(e)}
