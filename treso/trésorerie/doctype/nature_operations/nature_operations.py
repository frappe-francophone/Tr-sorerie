# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class NatureOperations(Document):

	def before_insert(self):
		if self.solde_initial == 1:
			exists = frappe.db.exists("Nature Operations", { "solde_initial": 1 })
			if exists:
				frappe.throw("Il existe déjà une nature de Solde initial") 

		#if self.echange == 1 and self.solde_initial == 1 :
		#	frappe.throw("Une même opération ne saurait être de nature échange et solde initial...")
	
	def before_save(self):
		#exists = frappe.db.exists("Nature Operations", { "solde_initial": 1 })
		#if exists:
		#	frappe.throw("Il existe déjà une nature de Solde initial") 

		if self.echange == 1 and self.solde_initial == 1 :
			frappe.throw("Une même opération ne saurait être de nature échange et solde initial...")

	 
