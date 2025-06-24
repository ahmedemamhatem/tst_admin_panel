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
    Return all website content sections and items, grouped by parent where relevant,
    with all URL fields as "" if not found.
    """
    try:
        content_list = frappe.get_all(
            'Website Content',
            fields=[
                'name', 'section_name', 'parent_website_content', 'is_group',
                'title_en', 'title_ar', 'content_en', 'content_ar', 'attachment',
                'background_image', 'video'
            ]
        )
        base_url = frappe.utils.get_url()

        def get_full_url(path):
            if path:
                if not path.startswith("/"):
                    path = "/" + path
                return base_url + path
            return ""

        # Index all items by name for easy lookup
        items_by_name = {item['name']: item for item in content_list}
        # Collect all children by their parent
        children_map = {}
        for item in content_list:
            parent = item.get('parent_website_content')
            if parent:
                children_map.setdefault(parent, []).append(item)

        sections = {}
        # Track which children have been nested so we don't output them twice
        nested_children_names = set()

        for item in content_list:
            # Parent section (is_group) or standalone (no parent)
            is_group = item.get("is_group")
            has_parent = bool(item.get("parent_website_content"))

            if is_group or not has_parent:
                section_key = item['section_name']
                # If this key already exists (multiple items with same section_name), make it a list
                section_obj = {
                    "titleEN": item.get("title_en", ""),
                    "titleAR": item.get("title_ar", ""),
                    "descriptionEN": item.get("content_en", ""),
                    "descriptionAR": item.get("content_ar", ""),
                    "imageUrl": get_full_url(item.get("attachment")),
                    "backgroundImageUrl": get_full_url(item.get("background_image")),
                    "videoUrl": get_full_url(item.get("video"))
                }

                # Attach all possible child groups dynamically
                children = children_map.get(item["name"], [])
                if children:
                    # Group children by their section_name
                    child_groups = {}
                    for child in children:
                        group_key = child['section_name']
                        child_obj = {
                            "titleEN": child.get("title_en", ""),
                            "titleAR": child.get("title_ar", ""),
                            "contentEN": child.get("content_en", ""),
                            "contentAR": child.get("content_ar", ""),
                            "imageUrl": get_full_url(child.get("attachment")),
                            "backgroundImageUrl": get_full_url(child.get("background_image")),
                            "videoUrl": get_full_url(child.get("video"))
                        }
                        child_groups.setdefault(group_key, []).append(child_obj)
                        nested_children_names.add(child['name'])
                    # Add child groups to section
                    for group_key, group_items in child_groups.items():
                        section_obj[group_key] = group_items

                # Support multiple items with same section_name (rare, but possible)
                if section_key in sections:
                    # If already a list, add to it
                    if isinstance(sections[section_key], list):
                        sections[section_key].append(section_obj)
                    else:
                        sections[section_key] = [sections[section_key], section_obj]
                else:
                    sections[section_key] = section_obj

        # Add any children that were not nested (orphans, or non-group non-parent)
        for item in content_list:
            if (
                not item.get("is_group") and
                not item.get("parent_website_content") and
                item['name'] not in nested_children_names
            ):
                section_key = item['section_name']
                child_obj = {
                    "titleEN": item.get("title_en", ""),
                    "titleAR": item.get("title_ar", ""),
                    "contentEN": item.get("content_en", ""),
                    "contentAR": item.get("content_ar", ""),
                    "imageUrl": get_full_url(item.get("attachment")),
                    "backgroundImageUrl": get_full_url(item.get("background_image")),
                    "videoUrl": get_full_url(item.get("video"))
                }
                # If already exists, append (handle duplicates)
                if section_key in sections:
                    if isinstance(sections[section_key], list):
                        sections[section_key].append(child_obj)
                    else:
                        sections[section_key] = [sections[section_key], child_obj]
                else:
                    sections[section_key] = child_obj

        frappe.local.response["http_status_code"] = 200
        return {"data": sections}

    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        frappe.log_error(message=str(e), title="Get Website Content API Error")
        return {"error": str(e)}


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
