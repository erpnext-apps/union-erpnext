# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
from frappe import _

def validate_unique_designation(doc, method):
	if doc.designation:
		employees_with_same_designation = frappe.db.sql("""select name, employee_name from `tabEmployee`
			where name!=%s and designation=%s""", (doc.name, doc.designation), as_dict=True)

		if employees_with_same_designation:
			employees_with_same_designation = ", ".join("{employee_name} ({name})".format(**d) for d in employees_with_same_designation)
			frappe.throw(_("""{0} "{1}" already assigned to other Employee(s): {2}""").format(
				doc.meta.get_label("designation"), doc.designation, employees_with_same_designation))

