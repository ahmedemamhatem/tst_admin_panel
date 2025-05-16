import frappe
import json
from frappe.utils.response import json_handler

@frappe.whitelist(allow_guest=True)
def get_website_content():
    """
    Fetch all website content with readable Arabic text.
    """
    try:
        # Fetch all website content
        content_list = frappe.get_all(
            'Website Content',
            fields=['name', 'section_name', 'content_en', 'content_ar', 'image']
        )

        # Build response
        response = {
            "status": "success",
            "message": "Content fetched successfully.",
            "data": content_list
        }

        # Return JSON without escaping Unicode
        frappe.local.response["http_status_code"] = 200
        return json.dumps(response, default=json_handler, ensure_ascii=False)

    except Exception as e:
        # Handle unexpected errors
        frappe.log_error(message=str(e), title="Get Website Content API Error")
        response = {
            "status": "error",
            "message": "An unexpected error occurred.",
            "error": str(e)
        }
        frappe.local.response["http_status_code"] = 500
        return json.dumps(response, default=json_handler, ensure_ascii=False)




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