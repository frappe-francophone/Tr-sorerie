# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Justification(Document):

	def validate(self):
		nb = frappe.db.count('Operation de Caisse', {"docstatus": 1, "justifie": 1, "name": self.operation})
		#test = frappe.db.get_list('Caisse Initialisation', filters = {"docstatus": 0, "caisse": self.caisse}, fields=["name"])
		if nb > 0 :
			#frappe.msgprint(str(test))
			frappe.throw("Cette opération a déjà été validée!")
	
	def on_submit(self):
		frappe.db.sql(
		"""
			UPDATE `tabOperation de Caisse`
			SET justifie = 1
			WHERE name = %s
		""", (self.operation)
	)

	def on_cancel(self):
		frappe.db.sql(
		"""
			UPDATE `tabOperation de Caisse`
			SET justifie = 0
			WHERE name = %s
		""", (self.operation)
	)

