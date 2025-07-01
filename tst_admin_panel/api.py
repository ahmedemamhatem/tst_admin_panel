import frappe
from frappe.utils.password import set_encrypted_password, check_password, update_password
import json
from frappe.utils.response import json_handler
from frappe.utils import get_url


@frappe.whitelist(allow_guest=True, methods=['POST'])
def set_website_content():
    import frappe
    import json

    # --- Helper to get JSON payload ---
    try:
        data = frappe.local.form_dict
        if not data or not isinstance(data, dict):
            # Try as raw body
            data = json.loads(frappe.request.data)
    except Exception:
        data = {}

    # --- Helper: safe get, default to empty dict if missing ---
    def get_section(name):
        return data.get(name, {})

    # --- Helper: update fields on doc ---
    def update_fields(doc, mapping, input_data):
        for target_field, input_field in mapping.items():
            if input_field in input_data:
                setattr(doc, target_field, input_data[input_field])

    # --- About Us Section ---
    about_us_data = get_section("aboutUsSectionData")
    if about_us_data:
        doc = frappe.get_single("About Us Section")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
            "subtitlear": "subTitleAR",
            "subtitleen": "subTitleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, about_us_data)
        # Clear child table
        doc.set("about_us_tabs", [])
        doc.set("aboutus_tabs", [])
        for tab in about_us_data.get("aboutUSTabs", []):
            doc.append("aboutus_tabs", {
                "tablabelar": tab.get("tabLabelAR", ""),
                "tablabelen": tab.get("tabLabelEN", ""),
                "titlear": tab.get("titleAR", ""),
                "titleen": tab.get("titleEN", ""),
                "descriptionar": tab.get("descriptionAR", ""),
                "descriptionen": tab.get("descriptionEN", ""),
                "mediaurl": tab.get("mediaURL", ""),
                "mediatype": tab.get("mediaType", ""),
            })
        doc.save(ignore_permissions=True)

    # --- Branches Section ---
    branches_data = get_section("branchesSectionData")
    if branches_data:
        doc = frappe.get_single("Branches Section")
        mapping = {
            "maintitlear": "mainTitleAR",
            "maintitleen": "mainTitleEN",
            "subtitlear": "subTitleAR",
            "subtitleen": "subTitleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, branches_data)
        doc.set("branches", [])
        for branch in branches_data.get("branches", []):
            loc = branch.get("location", {}) or {}
            doc.append("branches", {
                "branchnamear": branch.get("branchNameAR", ""),
                "branchnameen": branch.get("branchNameEN", ""),
                "addressar": branch.get("addressAR", ""),
                "addressen": branch.get("addressEN", ""),
                "phone": branch.get("phone", ""),
                "hotline": branch.get("hotLine", ""),  
                "descriptionar": branch.get("descriptionAR", ""),
                "descriptionen": branch.get("descriptionEN", ""),
                "lat": loc.get("lat", None),
                "lng": loc.get("lng", None),
            })
        doc.save(ignore_permissions=True)

    # --- Activity Trackers Section ---
    activity_trackers_data = get_section("activityTrackersData")
    if activity_trackers_data:
        doc = frappe.get_single("Activity Trackers")
        mapping = {
            "maintitlear": "mainTitleAR",
            "maintitleen": "mainTitleEN",
        }
        update_fields(doc, mapping, activity_trackers_data)
        doc.set("activity_trackers", [])
        for row in activity_trackers_data.get("data", []):
            doc.append("activity_trackers", {
                "labelar": row.get("labelAR", ""),
                "labelen": row.get("labelEN", ""),
                "value": row.get("value", 0),
                "color": row.get("color", ""),
                "percentage": row.get("percentage", 0),
            })
        doc.save(ignore_permissions=True)

    # --- Device Installations Regions Section ---
    device_installations_data = get_section("deviceInstallationsRegionsData")
    if device_installations_data:
        doc = frappe.get_single("Device Installations Regions")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
        }
        update_fields(doc, mapping, device_installations_data)
        chart = device_installations_data.get("chartData", {})
        doc.set("region_chart_data", [])
        for i, label in enumerate(chart.get("labels", [])):
            dataset = chart.get("datasets", [{}])[0]
            doc.append("region_chart_data", {
                "label": label,
                "value": dataset.get("data", [])[i] if i < len(dataset.get("data", [])) else 0,
                "backgroundcolor": dataset.get("backgroundColor", [])[i] if i < len(dataset.get("backgroundColor", [])) else "",
                "hoverbackgroundcolor": dataset.get("hoverBackgroundColor", [])[i] if i < len(dataset.get("hoverBackgroundColor", [])) else "",
            })
        doc.save(ignore_permissions=True)

    # --- Project Achievements Section ---
    project_achievements_data = get_section("projectAchievementsData")
    if project_achievements_data:
        doc = frappe.get_single("Project Achievements")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, project_achievements_data)
        doc.set("achievement", [])  # Clear existing
        for item in project_achievements_data.get("achievements", []):
            doc.append("achievement", {
                "iconurl": item.get("iconURL", ""),   
                "value": item.get("value", 0),
                "labelar": item.get("labelAR", ""),
                "labelen": item.get("labelEN", "")
            })
        doc.save(ignore_permissions=True)
    
    # --- Our Solutions Section ---
    our_solutions_data = get_section("ourSolutionsData")
    if our_solutions_data:
        doc = frappe.get_single("Our Solutions")
        mapping = {
            "titleen": "titleEN",
            "titlear": "titleAR",
            "descriptionen": "descriptionEN",
            "descriptionar": "descriptionAR",
        }
        update_fields(doc, mapping, our_solutions_data)
        doc.set("solution", [])
        for s in our_solutions_data.get("solutions", []):
            doc.append("solution", {
                "imageurl": s.get("imageURL", ""),          
                "descriptionar": s.get("descriptionAR", ""),
                "descriptionen": s.get("descriptionEN", "")
            })
        doc.save(ignore_permissions=True)


    # --- Partners Section ---
    partners_data = get_section("partnersSectionData")
    if partners_data:
        doc = frappe.get_single("Partners Section")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, partners_data)
        doc.set("partners_tab", [])
        for tab in partners_data.get("partnersTabs", []):
            doc.append("partners_tab", {
                "titlear": tab.get("titleAR", ""),
                "titleen": tab.get("titleEN", ""),
                "image": tab.get("image", "")
            })
        doc.save(ignore_permissions=True)

    # --- Suppliers Section ---
    suppliers_data = get_section("suppliersSectionData")
    if suppliers_data:
        doc = frappe.get_single("Suppliers Section")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, suppliers_data)
        doc.set("company_logos", [])
        for img in suppliers_data.get("companiesLogos", []):
            doc.append("company_logo", {"logo": img})
        doc.save(ignore_permissions=True)

    # --- FAQ Section ---
    faq_data = get_section("faqSectionData")
    if faq_data:
        doc = frappe.get_single("FAQ Section")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
        }
        update_fields(doc, mapping, faq_data)
        doc.set("questions", [])
        for q in faq_data.get("questions", []):
            doc.append("questions", {
                "questionar": q.get("questionAR", ""),
                "answerar": q.get("answerAR", ""),
                "questionen": q.get("questionEN", ""),
                "answeren": q.get("answerEN", ""),
            })
        doc.save(ignore_permissions=True)

    # --- Testimonials Section ---
    testimonials_data = get_section("testimonialsSectionData")
    if testimonials_data:
        doc = frappe.get_single("Testimonials Section")
        mapping = {
            "titlear": "titleAR",
            "titleen": "titleEN",
            "descriptionar": "descriptionAR",
            "descriptionen": "descriptionEN",
        }
        update_fields(doc, mapping, testimonials_data)
        doc.set("company_logos", [])
        for img in testimonials_data.get("companiesLogos", []):
            doc.append("company_logo", {"logo": img})
        doc.set("testimonial", [])  # Clear existing testimonials if desired
        for t in data.get("testimonials", []):  # Your input key can be "testimonials"
            doc.append("testimonial", {
                "namear": t.get("nameAR", ""),
                "positionar": t.get("positionAR", ""),
                "rate": t.get("rate", 0),
                "nameen": t.get("nameEN", ""),
                "positionen": t.get("positionEN", ""),
                "feedbackar": t.get("feedbackAR", ""),
                "feedbacken": t.get("feedbackEN", "")
            })
        doc.save(ignore_permissions=True)

    return {"status": "success", "message": "Website content updated successfully"}



@frappe.whitelist(allow_guest=True)
def get_website_content():
    import frappe
    from frappe.utils import get_url

    base_url = get_url()

    def full_url(path):
        if not path:
            return ""
        if path.startswith("http"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return base_url + path

    try:
        # 1. About Us Section (child table accessed as attribute)
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

        # 2. Branches Section
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

        # 3. Activity Trackers Section
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

        # 4. Device Installations Regions Section
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

        # 5. Project Achievements Section
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
                    "iconURL": getattr(row, "iconurl", ""),
                    "labelAR": getattr(row, "labelar", ""),
                    "labelEN": getattr(row, "labelen", ""),
                    "value": getattr(row, "value", 0),
                }
                for i, row in enumerate(achievement_rows)
            ],
        }

        # 6. Our Solutions Section
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

        # 7. Partners Section
        partners = frappe.get_single("Partners Section")
        partners_tabs_rows = getattr(partners, "partners_tab", [])
        partners_tabs = []
        for i, tab in enumerate(partners_tabs_rows, 1):
            # If you have a child table for images under each tab:
            images_rows = getattr(tab, "partners_tab_images", [])
            images = [full_url(getattr(img, "image", "")) for img in images_rows if getattr(img, "image", "")]
            partners_tabs.append({
                "id": i,
                "titleAR": getattr(tab, "titlear", ""),
                "titleEN": getattr(tab, "titleen", ""),
                "images": images,
            })
        partners_section = {
            "titleAR": getattr(partners, "titlear", ""),
            "titleEN": getattr(partners, "titleen", ""),
            "descriptionAR": getattr(partners, "descriptionar", ""),
            "descriptionEN": getattr(partners, "descriptionen", ""),
            "partnersTabs": partners_tabs,
        }

        # 8. Suppliers Section
        suppliers = frappe.get_single("Suppliers Section")
        suppliers_logos_rows = getattr(suppliers, "company_logo", [])
        companies_logos = [full_url(getattr(row, "logo", "")) for row in suppliers_logos_rows if getattr(row, "logo", "")]
        suppliers_section = {
            "titleAR": getattr(suppliers, "titlear", ""),
            "titleEN": getattr(suppliers, "titleen", ""),
            "descriptionAR": getattr(suppliers, "descriptionar", ""),
            "descriptionEN": getattr(suppliers, "descriptionen", ""),
            "companiesLogos": companies_logos,
        }

        # 9. FAQ Section
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

        # 10. Testimonials Section
        testimonials = frappe.get_single("Testimonials Section")
        testimonials_logos_rows = getattr(testimonials, "company_logo", [])
        testimonials_companies_logos = [full_url(getattr(row, "logo", "")) for row in testimonials_logos_rows if getattr(row, "logo", "")]
        testimonials_rows = getattr(testimonials, "testimonial", [])
        testimonials_section = {
            "titleAR": getattr(testimonials, "titlear", ""),
            "titleEN": getattr(testimonials, "titleen", ""),
            "descriptionAR": getattr(testimonials, "descriptionar", ""),
            "descriptionEN": getattr(testimonials, "descriptionen", ""),
            "companiesLogos": testimonials_companies_logos,
            "testimonials": [
                {
                    "id": i + 1,
                    "nameAR": getattr(row, "namear", ""),
                    "nameEN": getattr(row, "nameen", ""),
                    "positionAR": getattr(row, "positionar", ""),
                    "positionEN": getattr(row, "positionen", ""),
                    "feedbackAR": getattr(row, "feedbackar", ""),
                    "feedbackEN": getattr(row, "feedbacken", ""),
                    "rate": getattr(row, "rate", 0),
                }
                for i, row in enumerate(testimonials_rows)
            ],
        }

        frappe.local.response["http_status_code"] = 200
        return {
            "aboutUsSectionData": about_us_section,
            "branchesSectionData": branches_section,
            "activityTrackersData": activity_trackers_section,
            "deviceInstallationsRegionsData": device_installations_section,
            "projectAchievementsData": project_achievements_section,
            "ourSolutionsData": our_solutions_section,
            "partnersSectionData": partners_section,
            "suppliersSectionData": suppliers_section,
            "faqSectionData": faq_section,
            "testimonialsSectionData": testimonials_section,
        }

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
        update_password(doc.user_name, doc.password)
        doc.password = None




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
