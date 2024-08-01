# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class AxeAnalytique(Document):
	
	def before_save(self):
		if not self.correspondance :
			self.correspondance = self.libelle