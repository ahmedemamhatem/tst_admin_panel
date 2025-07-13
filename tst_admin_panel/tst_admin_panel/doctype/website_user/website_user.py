# Copyright (c) 2025, Ahmed Emam and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password

class WebsiteUser(Document):
    def before_save(self):
        if self.password:
			
            update_password(self.name, self.password, doctype="Website User", fieldname="password")


