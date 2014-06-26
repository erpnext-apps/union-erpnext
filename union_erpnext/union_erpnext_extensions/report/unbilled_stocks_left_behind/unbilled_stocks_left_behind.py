
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import time,datetime
from datetime import date, timedelta
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	invoice_entries = get_invoice(filters)
	invoice_entries_less = get_invoice(filters)
	data = []
	total_invoice_qty = 0.0
	total_invoice_qty_less = 0.0
	less_qty = 0.0
	for in_individual in invoice_entries:
		flag = 0
		total_invoice_qty =  get_invoice_qty(in_individual.sales_order,in_individual.item_code,in_individual.posting_date,in_individual.posting_time)
		if in_individual.billing_status == 'Partly Billed':
			in_individual.qty = in_individual.qty - flt(total_invoice_qty[0].total_invoice_qty)


		inventory_entries = get_item_inventory(filters,in_individual.item_code,in_individual.warehouse)
		remain_qty = inventory_entries - in_individual.qty
		total_inventory = inventory_entries - in_individual.qty
		if in_individual.qty != 0:
			for check_invoice_qty in invoice_entries_less:
				if in_individual.sales_order == check_invoice_qty.sales_order and in_individual.item_code == check_invoice_qty.item_code and \
				 in_individual.warehouse == check_invoice_qty.warehouse and in_individual.posting_date == check_invoice_qty.posting_date:
					total_invoice_qty_less =  get_invoice_qty(check_invoice_qty.sales_order,check_invoice_qty.item_code,\
					check_invoice_qty.posting_date,check_invoice_qty.posting_time)
					less_qty  = check_invoice_qty.qty - flt(total_invoice_qty_less[0].total_invoice_qty)
					if in_individual.qty >  less_qty:
						flag = 1
			if flag == 0:
				data.append([in_individual.item_code,in_individual.qty,inventory_entries,remain_qty,in_individual.customer_name,in_individual.sales_order,in_individual.warehouse,in_individual.posting_date])


	return columns,data
def get_columns():
	return ["Item Code::100", "Qty Not Invoiced::150","Prev Day Ending Inv::150",
		"Net Inventory if Served::150","Customer Name::150","Sales Order ID::100",
		"Warehouse Name::150","Posting Date::100"]


def get_invoice(filters):
	warehouse = str(filters.get("warehouse"))
	posting_date = str(filters.get("posting_date"))
	return frappe.db.sql("""
		select
			si.posting_time, so.customer_name, si_item.sales_order, si_item.warehouse,
			so_item.item_code, so_item.qty, so.billing_status, si.posting_date, si_item.qty as invoice_qty
		from `tabSales Invoice` as si, `tabSales Invoice Item` si_item ,
			`tabSales Order` so ,`tabSales Order Item` so_item
		where
			si.name = si_item.parent
			and si_item.sales_order = so.name
			and so_item.parent = si_item.sales_order
			and so.billing_status != 'Fully Billed'
			and si_item.item_code = so_item.item_code
			and si.docstatus = 1
			{conditions}
		group by si.name,si_item.item_code
		order by si_item.item_code""".format(conditions=get_item_conditions(filters)),filters,as_dict=1)

def get_item_conditions(filters):
	conditions = ""
	if filters.get("warehouse"):
		conditions += " and si_item.warehouse = '%s' "%filters["warehouse"]
	if filters.get("posting_date"):
		conditions += " and si.posting_date = '%s' "%filters["posting_date"]

	return conditions


def get_stock_ledger_entries(filters,item_code,warehouse):
	posting_date  = str(filters.get("posting_date"))
	return frappe.db.sql("""
		select
			item_code, warehouse, posting_date, actual_qty
		from `tabStock Ledger Entry`
		where
			docstatus = 1 and
			item_code = '""" + item_code + """'
			and warehouse='""" + warehouse +"""'
			{conditions}
		order by item_code, warehouse
	""".format(conditions=get_inventory_conditions(filters)),filters,as_dict=1)

def get_item_inventory(filters,item_code,warehouse):
	sle = get_stock_ledger_entries(filters,item_code,warehouse)
	iwb_map = {}
	in_qty = 0.0
	out_qty = 0.0
	bal_qty= 0.0
	for d in sle:
		if flt(d.actual_qty) > 0:
			in_qty += flt(d.actual_qty)
		else:
			out_qty += abs(flt(d.actual_qty))
		bal_qty += flt(d.actual_qty)

	return bal_qty

def get_inventory_conditions(filters):
	yesterday = date.today()-timedelta(1)
	conditions = ""
	if filters.get("warehouse"):
		conditions += " and warehouse = '%s' "%filters["warehouse"]
	if filters.get("posting_date"):
		conditions += " and posting_date < '%s' "%filters["posting_date"]
	else:
		conditions += " and posting_date <= '%s' "%yesterday

	return conditions

def get_invoice_qty(sales_order,item_code,posting_date,posting_time):
	return frappe.db.sql("""
		select SUM(qty) as total_invoice_qty
		from `tabSales Invoice Item`  as si_item , `tabSales Invoice` as si
		where
			si_item.sales_order = '""" + sales_order + """' and si_item.item_code = '""" + item_code + """'
			and si.posting_date <= '""" + posting_date +"""' and si.posting_time <= '""" + posting_time +"""'
			and si_item.docstatus = 1 and si.docstatus =1 and si_item.parent = si.name""",as_dict=1)
