import frappe
from frappe.utils.password import set_encrypted_password, check_password, update_password
import json
from frappe.utils.response import json_handler

import frappe

def update_workspace_after_migration():
    """
    Update the Workspace to set 'Module' = 'Tst Admin Panel' where 'name' = 'TST Website'.
    """
    try:
        # Find the workspace with the name "TST Website"
        workspace_name = "TST Website"
        new_module = "Tst Admin Panel"

        # Update the workspace's module
        frappe.db.set_value("Workspace", workspace_name, "module", new_module)

        # Log success
        frappe.log_error(
            title="Workspace Updated",
            message=f"Updated Workspace '{workspace_name}' to Module '{new_module}'."
        )
        frappe.msgprint(
            f"Workspace '{workspace_name}' successfully updated to Module '{new_module}'."
        )
    except Exception as e:
        # Log and raise an error if something goes wrong
        frappe.log_error(
            title="Failed to Update Workspace",
            message=f"Error: {str(e)}"
        )
        frappe.throw(f"Failed to update Workspace: {str(e)}")


def before_save_user(doc, method):
    if doc.password:
        update_password(doc.user_name, doc.password)
        doc.password = None


@frappe.whitelist(allow_guest=True)
def get_website_content():
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

        items_by_name = {item['name']: item for item in content_list}
        children_map = {}
        for item in content_list:
            parent = item.get('parent_website_content')
            if parent:
                children_map.setdefault(parent, []).append(item)

        sections = {}
        added_keys = set()

        # Step 1: Add flat non-group sections first (no parent, not group)
        for item in content_list:
            if not item.get("is_group") and not item.get("parent_website_content"):
                section_key = item["section_name"]
                if section_key in added_keys:
                    continue

                obj = {
                    "titleEN": item.get("title_en", ""),
                    "titleAR": item.get("title_ar", ""),
                    "contentEN": item.get("content_en", ""),
                    "contentAR": item.get("content_ar", ""),
                    "imageUrl": get_full_url(item.get("attachment")),
                    "backgroundImageUrl": get_full_url(item.get("background_image")),
                    "videoUrl": get_full_url(item.get("video")),
                }
                sections[section_key] = obj
                added_keys.add(section_key)

        # Step 2: Add group sections and their children (nested)
        for item in content_list:
            if item.get("is_group"):
                section_key = item["section_name"]
                if section_key in added_keys:
                    continue

                section_obj = {
                    "titleEN": item.get("title_en", ""),
                    "titleAR": item.get("title_ar", ""),
                    "descriptionEN": item.get("content_en", ""),
                    "descriptionAR": item.get("content_ar", ""),
                    "imageUrl": get_full_url(item.get("attachment")),
                    "backgroundImageUrl": get_full_url(item.get("background_image")),
                    "videoUrl": get_full_url(item.get("video")),
                }

                children = children_map.get(item["name"], [])
                if children:
                    child_groups = {}
                    for child in children:
                        group_key = child["section_name"]
                        child_obj = {
                            "titleEN": child.get("title_en", ""),
                            "titleAR": child.get("title_ar", ""),
                            "contentEN": child.get("content_en", ""),
                            "contentAR": child.get("content_ar", ""),
                            "imageUrl": get_full_url(child.get("attachment")),
                            "backgroundImageUrl": get_full_url(child.get("background_image")),
                            "videoUrl": get_full_url(child.get("video")),
                        }
                        child_groups.setdefault(group_key, []).append(child_obj)

                    for group_key, group_items in child_groups.items():
                        section_obj[group_key] = group_items

                sections[section_key] = section_obj
                added_keys.add(section_key)

        # Optional: flatten single-item lists
        for key in list(sections.keys()):
            if isinstance(sections[key], list) and len(sections[key]) == 1:
                sections[key] = sections[key][0]

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
