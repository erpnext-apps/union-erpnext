from frappe import _

def get_data():
	return [
		{
			"label": _("Union Reports"),
			"icon": "icon-paper-clip",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Unbilled Stocks Left Behind",
					"doctype": "Sales Invoice",
				}
			]
		}
	]
