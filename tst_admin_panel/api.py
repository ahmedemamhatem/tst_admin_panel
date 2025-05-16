import frappe
from frappe.utils.password import set_encrypted_password, check_password, update_password
import json
from frappe.utils.response import json_handler

def before_save_user(doc, method):
    if doc.password:
        update_password(doc.user_name, doc.password)
        doc.password = None

@frappe.whitelist(allow_guest=True)
def get_website_content():
    """
    Fetch all website content with readable Arabic text.
    """
    try:
        # Fetch all website content
        content_list = frappe.get_all(
            'Website Content',
            fields=['section_name', 'content_en', 'content_ar', 'image']
        )

        # Return only the fetched data
        frappe.local.response["http_status_code"] = 200
        return json.dumps(content_list, default=json_handler, ensure_ascii=False)

    except Exception as e:
        # Return only the error message
        frappe.local.response["http_status_code"] = 500
        frappe.log_error(message=str(e), title="Get Website Content API Error")
        return json.dumps({"error": str(e)}, default=json_handler, ensure_ascii=False)


def insert_website_content():
    """
    Job to insert multiple records into the 'Website Content' Doctype.
    """
    # Define the records you want to insert
    records = [
        {
            "doctype": "Website Content",
            "section_name": "About Us",
            "content_en": "Welcome to our website!",
            "content_ar": "مرحبا بك في موقعنا!",
            "image": "/files/about-us.jpg"
        },
        {
            "doctype": "Website Content",
            "section_name": "Contact Us",
            "content_en": "Reach out to us anytime.",
            "content_ar": "تواصل معنا في أي وقت.",
            "image": "/files/contact-us.jpg"
        },
        {
            "doctype": "Website Content",
            "section_name": "Services",
            "content_en": "We offer a variety of services.",
            "content_ar": "نحن نقدم مجموعة متنوعة من الخدمات.",
            "image": "/files/services.jpg"
        }
    ]

    # Insert records into the database
    for record in records:
        if not frappe.db.exists("Website Content", {"section_name": record["section_name"]}):
            doc = frappe.get_doc(record)
            doc.insert()
            frappe.db.commit()  # Commit changes to the database
            print(f"Inserted record: {record['section_name']}")
        else:
            print(f"Record already exists: {record['section_name']}")


@frappe.whitelist(allow_guest=True)
def login_website_user(username, password):
    """
    API endpoint to verify website user login credentials.

    Args:
        username (str): The username of the Website User.
        password (str): The password of the Website User.

    Returns:
        JSON: Customer ID and permissions if login is successful, or an error message.
    """
    try:
        # Use direct SQL to fetch user data
        user_data = frappe.db.sql("""
            SELECT name, user_name, disabled, customer_id, permissions
            FROM `tabWebsite User`
            WHERE user_name = %s
            LIMIT 1
        """, (username,), as_dict=True)

        if not user_data:
            frappe.local.response["http_status_code"] = 401
            return {"error": "Invalid username or password."}

        user = user_data[0]

        if user.disabled == 1:
            frappe.local.response["http_status_code"] = 401
            return {"error": "User is disabled."}

        # Check the password using frappe's check_password
        try:
            check_password(user.user_name, password)
        except frappe.exceptions.AuthenticationError:
            frappe.local.response["http_status_code"] = 401
            return {"error": "Invalid username or password."}

        response = {
            "customer_id": user.customer_id,
            "permissions": user.permissions
        }
        frappe.local.response["http_status_code"] = 200
        return response

    except Exception as e:
        frappe.log_error(message=str(e), title="Website User Login Error")
        frappe.local.response["http_status_code"] = 500
        return {"error": "An unexpected error occurred."}



@frappe.whitelist(allow_guest=True)
def reset_password(username, new_password):
    """
    Reset the password for a Website User by directly updating the password field in the document.

    Args:
        username (str): The username of the Website User.
        new_password (str): The new password to be set.

    Returns:
        JSON: Success or error message.
    """
    try:
        # Use SQL to check if user exists and is enabled
        user_data = frappe.db.sql("""
            SELECT name, user_name, disabled
            FROM `tabWebsite User`
            WHERE user_name = %s
            LIMIT 1
        """, (username,), as_dict=True)

        if not user_data:
            frappe.local.response["http_status_code"] = 401
            return {"error": "Invalid username."}

        user = user_data[0]

        if user.disabled == 1:
            frappe.local.response["http_status_code"] = 401
            return {"error": "User is disabled."}

        # Use get_doc to update, since we need to set password
        user_doc = frappe.get_doc("Website User", user.name)
        user_doc.password = new_password
        user_doc.save(ignore_permissions=True)
        user_doc.reload()
        frappe.db.commit()

        frappe.local.response["http_status_code"] = 200
        return {"message": "Password reset successful."}

    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"error": "User not found."}
    except Exception as e:
        frappe.log_error(message=str(e), title="Password Reset Error")
        frappe.local.response["http_status_code"] = 500
        return {"error": "An unexpected error occurred."}
