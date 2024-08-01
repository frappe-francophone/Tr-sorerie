# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class DemandePaiement(Document):
	def validate(self):
		self.validate_nature()

	def validate_nature(self):
		for d in self.get("details_operation_de_caisse"):
			justifiable = frappe.db.get_value("Nature Operations", d.nature_operations, "justifiable")
			if justifiable == "Oui":
				if not (d.imputation_analytique):
					frappe.throw(_("Ligne {0}: Veuillez renseigner la nature analytique").format(d.idx))

			tiers = frappe.db.get_value("Nature Operations", d.nature_operations, "tiers")
			if tiers == "Oui":
				if not (d.tiers):
					frappe.throw(_("Ligne {0}: Veuillez renseigner le tiers").format(d.idx))
