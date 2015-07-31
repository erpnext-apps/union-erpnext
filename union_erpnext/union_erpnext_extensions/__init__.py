from __future__ import unicode_literals

import frappe

@frappe.whitelist()
def get_tma_campaign(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name from `tabCampaign` where proposal_status='Approved'
		and curdate() between start_date and end_date 
		and (customer = %s or national_campaign=1) order by name""", filters.get('customer_group'))
