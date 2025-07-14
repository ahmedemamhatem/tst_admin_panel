import frappe
from frappe.utils.password import set_encrypted_password, check_password, update_password
import json
from frappe.utils.response import json_handler
from frappe.utils import get_url
from frappe.utils import now
import jwt
import datetime
import os
import jwt
import datetime
from frappe.utils import now_datetime, add_to_date


@frappe.whitelist(allow_guest=True)
def login_website_user(username, password):
    try:
        user = frappe.db.get_value("Website User", {"user_name": username}, ["name", "customer_id", "permissions", "disabled"], as_dict=True)

        if not user:
            frappe.local.response["http_status_code"] = 401
            return {"error": "Invalid username or password"}

        if user.disabled:
            frappe.local.response["http_status_code"] = 401
            return {"error": "User is disabled"}

        try:
            check_password(user.name, password, doctype="Website User", fieldname="password")
        except (frappe.AuthenticationError, ValueError):
            frappe.local.response["http_status_code"] = 401
            return {"error": "Incorrect username or password"}

        # JWT generation
        import jwt, datetime
        SECRET_KEY = frappe.conf.encryption_key
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

        payload = {
            "username": username,
            "customer_id": user.customer_id,
            "permissions": user.permissions,
            "exp": int(expiration.timestamp())
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        frappe.db.set_value("Website User", user.name, {
            "token": token,
            "exp": expiration
        })

        return {
            "customer_id": user.customer_id,
            "permissions": user.permissions,
            "token": token
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Login Error")
        frappe.local.response["http_status_code"] = 500
        return {"error": f"{e.__class__.__name__}: {str(e)}"}




@frappe.whitelist(allow_guest=True)  
def insert_contact():
    """
    Dynamically accept all incoming data and insert it into the 'Contact Us' doctype.

    Returns:
        dict: The inserted document.
    """
    # Get all data from the request
    data = frappe.local.form_dict

    # Ensure required fields are present
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")
    contact_number = data.get("contactNumber")

    if not email or not subject or not message or not contact_number:
        frappe.throw("Fields `email`, `subject`, `message`, and `contact_number` are required!")

    # Create a new document dynamically using the data received
    doc = frappe.get_doc({
        "doctype": "Contact Us",
        "email": email,
        "subject": subject,
        "message": message,
        "contact_number": contact_number,
        "creation": now(),
        "modified": now(),
        "modified_by": frappe.session.user or "Guest",
        "owner": frappe.session.user or "Guest",
        # Include any additional fields dynamically
        **{key: value for key, value in data.items() if key not in ["email", "subject", "message", "contact_number"]}
    })

    # Insert into the database
    doc.insert(ignore_permissions=True)
    frappe.db.commit()


def clear_website_content_cache(doc=None, method=None):
    import frappe
    cache_key = "website_content_json"
    frappe.cache().delete_value(cache_key)

@frappe.whitelist(allow_guest=True)
def get_website_content():
    cache_key = "website_content_json"
    cache_ttl = 86400  # Cache expiration time in seconds (1 day)

    # --- 1. Attempt to serve from cache ---
    cached = frappe.cache().get_value(cache_key)
    if cached:
        frappe.local.response["http_status_code"] = 200
        return frappe.parse_json(cached)

    # --- 2. Helper to construct full URLs ---
    def full_url(path):
        if not path:
            return ""
        if path.startswith("http"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return get_url() + path

    try:
        # === 8. Partners Section (multi-level) ===
        partners_section_doc = frappe.get_single("Partners Section")
        partners_rows = getattr(partners_section_doc, "partners_tab", [])
        partners_tabs = []
        for i, partners_row in enumerate(partners_rows, 1):
            partners_tab_name = getattr(partners_row, "partners_tab", None)
            if not partners_tab_name:
                continue
            partners_tab_doc = frappe.get_doc("Partners Tab", partners_tab_name)
            images_rows = getattr(partners_tab_doc, "image", [])
            images = [
                full_url(getattr(img, "attach", ""))
                for img in images_rows if getattr(img, "attach", "")
            ]
            partners_tabs.append({
                "id": i,
                "titleAR": getattr(partners_tab_doc, "titlear", ""),
                "titleEN": getattr(partners_tab_doc, "titleen", ""),
                "images": images,
            })
        partners_section = {
            "titleAR": getattr(partners_section_doc, "titlear", ""),
            "titleEN": getattr(partners_section_doc, "titleen", ""),
            "descriptionAR": getattr(partners_section_doc, "descriptionar", ""),
            "descriptionEN": getattr(partners_section_doc, "descriptionen", ""),
            "partnersTabs": partners_tabs,
        }

        # === 9. Suppliers Section ===
        suppliers = frappe.get_single("Suppliers Section")
        suppliers_logos_rows = getattr(suppliers, "company_logo", [])
        companies_logos = [
            full_url(getattr(row, "logo", "")) 
            for row in suppliers_logos_rows if getattr(row, "logo", "")
        ]
        suppliers_section = {
            "titleAR": getattr(suppliers, "titlear", ""),
            "titleEN": getattr(suppliers, "titleen", ""),
            "descriptionAR": getattr(suppliers, "descriptionar", ""),
            "descriptionEN": getattr(suppliers, "descriptionen", ""),
            "companiesLogos": companies_logos,
        }
        
        # === 1. Banner Section ===
        banner = frappe.get_single("Banner Section")
        banner_section = {
            "titleEN": getattr(banner, "titleen", ""),
            "titleAR": getattr(banner, "titlear", ""),
            "subtitleEN": getattr(banner, "subtitleen", ""),
            "subtitleAR": getattr(banner, "subtitlear", ""),
            "descriptionAR": getattr(banner, "descriptionar", ""),
            "descriptionEN": getattr(banner, "descriptionen", ""),
            "backgroundImageUrl": full_url(getattr(banner, "background_image", "")),
            "videoUrl": full_url(getattr(banner, "video", "")),
        }

        # === 2. About Us Section ===
        about_us = frappe.get_single("About Us Section")
        about_us_tabs = getattr(about_us, "aboutus_tabs", [])
        about_us_section = {
            "titleAR": getattr(about_us, "titlear", ""),
            "titleEN": getattr(about_us, "titleen", ""),
            "subTitleAR": getattr(about_us, "subtitlear", ""),
            "subTitleEN": getattr(about_us, "subtitleen", ""),
            "descriptionAR": getattr(about_us, "descriptionar", ""),
            "descriptionEN": getattr(about_us, "descriptionen", ""),
            "aboutUSTabs": [
                {
                    "id": i + 1,
                    "tabLabelAR": getattr(tab, "tablabelar", ""),
                    "tabLabelEN": getattr(tab, "tablabelen", ""),
                    "titleAR": getattr(tab, "titlear", ""),
                    "titleEN": getattr(tab, "titleen", ""),
                    "descriptionAR": getattr(tab, "descriptionar", ""),
                    "descriptionEN": getattr(tab, "descriptionen", ""),
                    "mediaType": getattr(tab, "mediatype", ""),
                    "mediaURL": full_url(getattr(tab, "mediaurl", "")),
                }
                for i, tab in enumerate(about_us_tabs)
            ]
        }

        # === 3. Branches Section ===
        branches = frappe.get_single("Branches Section")
        branches_list = getattr(branches, "branches", [])
        branches_section = {
            "mainTitleAR": getattr(branches, "maintitlear", ""),
            "mainTitleEN": getattr(branches, "maintitleen", ""),
            "subTitleAR": getattr(branches, "subtitlear", ""),
            "subTitleEN": getattr(branches, "subtitleen", ""),
            "descriptionAR": getattr(branches, "descriptionar", ""),
            "descriptionEN": getattr(branches, "descriptionen", ""),
            "branches": [
                {
                    "branchNameAR": getattr(row, "branchnamear", ""),
                    "branchNameEN": getattr(row, "branchnameen", ""),
                    "addressAR": getattr(row, "addressar", ""),
                    "addressEN": getattr(row, "addressen", ""),
                    "phone": getattr(row, "phone", ""),
                    "hotLine": getattr(row, "hotline", ""),
                    "descriptionAR": getattr(row, "descriptionar", ""),
                    "descriptionEN": getattr(row, "descriptionen", ""),
                    "location": {
                        "lat": getattr(row, "lat", ""),
                        "lng": getattr(row, "lng", ""),
                    }
                }
                for row in branches_list
            ]
        }

        # === 4. Activity Trackers Section ===
        activity_trackers = frappe.get_single("Activity Trackers")
        activity_rows = getattr(activity_trackers, "activity_trackers", [])
        activity_trackers_section = {
            "mainTitleAR": getattr(activity_trackers, "maintitlear", ""),
            "mainTitleEN": getattr(activity_trackers, "maintitleen", ""),
            "data": [
                {
                    "labelAR": getattr(row, "labelar", ""),
                    "labelEN": getattr(row, "labelen", ""),
                    "value": getattr(row, "value", 0),
                    "color": getattr(row, "color", ""),
                    "percentage": getattr(row, "percentage", 0),
                }
                for row in activity_rows
            ],
        }

        # === 5. Device Installations Regions Section ===
        device_installations = frappe.get_single("Device Installations Regions")
        region_rows = getattr(device_installations, "region_chart_data", [])
        chart_data = {
            "labels": [getattr(r, "label", "") for r in region_rows],
            "datasets": [{
                "data": [getattr(r, "value", 0) for r in region_rows],
                "backgroundColor": [getattr(r, "backgroundcolor", "") for r in region_rows],
                "hoverBackgroundColor": [getattr(r, "hoverbackgroundcolor", "") for r in region_rows],
            }]
        }
        device_installations_section = {
            "titleAR": getattr(device_installations, "titlear", ""),
            "titleEN": getattr(device_installations, "titleen", ""),
            "chartData": chart_data
        }

        # === 6. Project Achievements Section ===
        achievements = frappe.get_single("Project Achievements")
        achievement_rows = getattr(achievements, "achievement", [])
        project_achievements_section = {
            "titleAR": getattr(achievements, "titlear", ""),
            "titleEN": getattr(achievements, "titleen", ""),
            "descriptionAR": getattr(achievements, "descriptionar", ""),
            "descriptionEN": getattr(achievements, "descriptionen", ""),
            "achievements": [
                {
                    "id": i + 1,
                    "iconURL": full_url(getattr(row, "iconurl", "")),
                    "icon": full_url(getattr(row, "iconurl", "")),
                    "labelAR": getattr(row, "labelar", ""),
                    "labelEN": getattr(row, "labelen", ""),
                    "value": getattr(row, "value", 0),
                }
                for i, row in enumerate(achievement_rows)
            ],
        }

        # === 7. Our Solutions Section ===
        solutions = frappe.get_single("Our Solutions")
        solution_rows = getattr(solutions, "solution", [])
        our_solutions_section = {
            "titleEN": getattr(solutions, "titleen", ""),
            "titleAR": getattr(solutions, "titlear", ""),
            "descriptionEN": getattr(solutions, "descriptionen", ""),
            "descriptionAR": getattr(solutions, "descriptionar", ""),
            "solutions": [
                {
                    "id": i + 1,
                    "imageURL": full_url(getattr(row, "imageurl", "")),
                    "descriptionAR": getattr(row, "descriptionar", ""),
                    "descriptionEN": getattr(row, "descriptionen", ""),
                }
                for i, row in enumerate(solution_rows)
            ],
        }

        # === 8. Social Media Links Section ===
        social_media_links = frappe.get_single("Social Media Links")
        social_media_links_table = getattr(social_media_links, "links", [])

        # Map the child table data
        social_media_links_section = [
            {
                "title": link.get("title", ""),
                "url": link.get("url", ""),
                "icon": get_url(link.get("icon", "")) if link.get("icon") else ""
            }
            for link in social_media_links_table
        ]
        
        # === 9. FAQ Section ===
        faq = frappe.get_single("FAQ Section")
        faq_questions_rows = getattr(faq, "questions", [])
        faq_section = {
            "titleAR": getattr(faq, "titlear", ""),
            "titleEN": getattr(faq, "titleen", ""),
            "questions": [
                {
                    "id": i + 1,
                    "questionAR": getattr(row, "questionar", ""),
                    "questionEN": getattr(row, "questionen", ""),
                    "answerAR": getattr(row, "answerar", ""),
                    "answerEN": getattr(row, "answeren", ""),
                }
                for i, row in enumerate(faq_questions_rows)
            ]
        }

        # --- 3. Build and cache the result ---
        result = {
            "bannerSection": banner_section,
            "aboutUsSectionData": about_us_section,
            "branchesSectionData": branches_section,
            "activityTrackersData": activity_trackers_section,
            "deviceInstallationsRegionsData": device_installations_section,
            "projectAchievementsData": project_achievements_section,
            "ourSolutionsData": our_solutions_section,
            "faqSectionData": faq_section,
            "partnersSectionData": partners_section,
            "suppliersSectionData": suppliers_section,
            "socialMediaLinksData": social_media_links_section,
        }

        frappe.cache().set_value(cache_key, frappe.as_json(result), expires_in_sec=cache_ttl)
        frappe.local.response["http_status_code"] = 200
        return result

    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        frappe.log_error(frappe.get_traceback(), "get_website_content error")
        return {"error": str(e)}


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
        update_password(doc.name, doc.password, doctype="Website User", fieldname="password")
        doc.password = None  # Hide raw password
    frappe.msgprint("Password updated successfully.")


@frappe.whitelist(allow_guest=True)
def get_website_content_old():
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
