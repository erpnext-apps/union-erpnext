// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors

frappe.query_reports["Unbilled Stocks Left Behind"] = {
        "filters": [
                {
                        "fieldname":"warehouse",
                        "label": frappe._("Warehouse"),
                        "fieldtype": "Link",
                        "options": "Warehouse"
                },
                {
                         "fieldname":"posting_date",
                        "label": frappe._("Posting Date"),
                        "Default":frappe.datetime.get_today(),
                        "fieldtype": "Date",
                        "options": "Posting Date"
                }
        ]
}
