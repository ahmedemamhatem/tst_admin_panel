// Copyright (c) 2025, Ahmed Emam and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Website Content", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Website Content", {
    onload: function (frm) {
        frm.set_query("parent_website_content", function () {
            return {
                filters: [
                    ["is_group", "=", 1], // Only include records where is_group = 1
                    ["name", "!=", frm.doc.name] // Exclude the current record
                ]
            };
        });
    }
});