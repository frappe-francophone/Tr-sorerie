# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from treso.trésorerie.doctype.devise.devise import get_billetage

class Caisse(Document):

	def before_save(self):
		self.solde = 0

	def before_submit(self):
		pass
		#self.solde = self.solde_initial
		#self.date_solde = self.date_lancement
	
	def on_submit(self):
		if self.solde_initial == 0:
			return
			
		billetage = []
		for billet in self.billetage:
			sub_args = frappe._dict({
				"doctype": "Billetage",
				"nom": billet.nom,
				"unite": billet.unite,
				#"image": billet.image,
				"nombre_initial": billet.nombre_initial,
				"valeur_initiale": billet.valeur_initiale,
				"nombre_final": billet.nombre_final,
				"valeur_finale": billet.valeur_finale,
				"parrenttype": "Caisse Initialisation",
				"parentfield": "billetage",
			})
			billetage.append(sub_args)
		
		args = frappe._dict(
			{
				"doctype": "Caisse Initialisation",
				"caisse": self.name,
				"initialisation": 1,
				"date_initialisation": self.date_lancement,
				"date_fermeture": self.date_lancement,
				"devise": self.devise,
				"cours": self.cours,
				"solde_initial": 0,
				"solde_final": 0,
				"billetage": billetage,
			}
		)

		caisse_init = frappe.get_doc(args)
		caisse_init.insert()
		
		# Remplissage de l'opération de compte de solde initial
		init = frappe.db.sql(
			"""
			SELECT name
			FROM `tabNature Operations`
			WHERE solde_initial = 1
			"""
		)[0][0]

		operation_sub = []
		sub_args = frappe._dict({
			"doctype": "Details Operation de Caisse",
			"nature_operations": init,
			"montant_devise": self.solde_initial,
			"montant_devise_ref":self.solde_initial,
			"devise": self.devise,
			"devise_caisse": self.devise,
			"cours": self.cours,
			"parrenttype": "Encaissement",
			"parentfield": "details_operation_de_caisse",
		})
		operation_sub.append(sub_args)

		year = str(getdate(self.date_lancement).year)
		month = str(getdate(self.date_lancement).month)
		if len(month) == 1:
			month = '0' + month
		code = year[2:] + self.name + month + 'ENC' + '00000'

		args = frappe._dict(
			{
				"doctype": "Encaissement",
				"caisse": self.name,
				"code_operation": code,
				"initialisation": caisse_init.name,
				"designation": "Solde Initial",
				"date": self.date_lancement,
				"devise": self.devise,
				"cours": self.cours,
				"remettant": frappe.session.user,
				"montant": self.solde_initial,
				"montant_reference": self.solde_initial,
				"details_operation_de_caisse": operation_sub,
			}
		)

		ci_name = caisse_init.name

		operation = frappe.get_doc(args)
		operation.submit()
		caisse_init = frappe.get_doc("Caisse Initialisation",ci_name)
		caisse_init.submit()


	@frappe.whitelist()
	def fill_billetage(self):
		
		for c in self.billetage :
			frappe.delete_doc("Billetage", c.name)

		billetage = get_billetage(self.devise)
		caisse_sub = []
		for b in billetage :
			billet = frappe._dict({
				"doctype": "Billetage",
				#"image": b.image,
				"nom": b.nom,
				"unite":b.unite,
				"nombre_initial": 0,
				"valeur_initiale": 0,
				"nombre_final": 0,
				"valeur_finale": 0,
				"parrenttype": "Caisse",
				"parentfield": "billetage",
				"parent": self.name,
			})
			caisse_sub.append(billet)

		#frappe.msgprint(str(self.billetage))
		doc = frappe.get_doc("Caisse", self.name)
		doc.billetage.append(caisse_sub)
		doc.save()


