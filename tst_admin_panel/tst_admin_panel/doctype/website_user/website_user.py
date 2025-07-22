# Copyright (c) 2025, Ahmed Emam and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils.password import update_password

class WebsiteUser(Document):
    def before_save(self):
        # Check if the `new_password` field is set
        if self.new_password:
            # Set the `password` field to the value of `new_password`
            self.password = self.new_password
            
            # Clear the `new_password` field
            self.new_password = None


