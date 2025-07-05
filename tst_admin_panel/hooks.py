app_name = "tst_admin_panel"
app_title = "Tst Admin Panel"
app_publisher = "Ahmed Emam"
app_description = "tst_admin_panel"
app_email = "ahmedemamhatem@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []
doc_events = {
    "Website User": {
        "before_save": "tst_admin_panel.api.before_save_user"
    }
}

after_migrate = [
    "tst_admin_panel.api.update_workspace_after_migration"
]

doc_events = {
    "Partners Section": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "Banner Section": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "About Us Section": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "Our Solutions": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "Branches Section": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "FAQ Section": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "Activity Trackers": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
    "Project Achievements": {
        "on_update": "tst_admin_panel.api.clear_website_content_cache",
        "on_trash": "tst_admin_panel.api.clear_website_content_cache",
    },
}

# fixtures = [
#     {
#         "doctype": "Workspace",
#         "filters": [
#             ["name", "=", "TST Website"]
#         ]
#     }
# ]
# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tst_admin_panel",
# 		"logo": "/assets/tst_admin_panel/logo.png",
# 		"title": "Tst Admin Panel",
# 		"route": "/tst_admin_panel",
# 		"has_permission": "tst_admin_panel.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tst_admin_panel/css/tst_admin_panel.css"
# app_include_js = "/assets/tst_admin_panel/js/tst_admin_panel.js"

# include js, css files in header of web template
# web_include_css = "/assets/tst_admin_panel/css/tst_admin_panel.css"
# web_include_js = "/assets/tst_admin_panel/js/tst_admin_panel.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tst_admin_panel/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tst_admin_panel/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tst_admin_panel.utils.jinja_methods",
# 	"filters": "tst_admin_panel.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tst_admin_panel.install.before_install"
# after_install = "tst_admin_panel.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tst_admin_panel.uninstall.before_uninstall"
# after_uninstall = "tst_admin_panel.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tst_admin_panel.utils.before_app_install"
# after_app_install = "tst_admin_panel.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tst_admin_panel.utils.before_app_uninstall"
# after_app_uninstall = "tst_admin_panel.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tst_admin_panel.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tst_admin_panel.tasks.all"
# 	],
# 	"daily": [
# 		"tst_admin_panel.tasks.daily"
# 	],
# 	"hourly": [
# 		"tst_admin_panel.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tst_admin_panel.tasks.weekly"
# 	],
# 	"monthly": [
# 		"tst_admin_panel.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "tst_admin_panel.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tst_admin_panel.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tst_admin_panel.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tst_admin_panel.utils.before_request"]
# after_request = ["tst_admin_panel.utils.after_request"]

# Job Events
# ----------
# before_job = ["tst_admin_panel.utils.before_job"]
# after_job = ["tst_admin_panel.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tst_admin_panel.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

