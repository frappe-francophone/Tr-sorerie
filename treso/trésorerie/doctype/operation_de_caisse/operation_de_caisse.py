# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils import flt
import json

import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from treso.trésorerie.doctype.devise.devise import get_cours

#from ls_treso.ls_treso.doctype.decaissement.decaissement import get_decaissement_route

class OperationdeCaisse(Document):

	def validate(self):
		self.date = frappe.utils.getdate(self.date)
		#self.validate_nature()
		
	def before_save(self):
		if len(self.details_operation_de_caisse) == 0:
			frappe.throw("Veuillez saisir au moins une ligne détail")

		exist = frappe.db.exists({
			"doctype": "Caisse Initialisation", 
			"name": self.initialisation,
			"docstatus": 1
		})
		if exist:
			frappe.throw("Vous ne pouvez enregistrer d'opérations sur le Numéro: " + self.initialisation + ". Veuillez choisir un numéro valide!")
		
		date_init = getdate(frappe.db.get_value('Caisse Initialisation', self.initialisation, 'date_initialisation'))
		date_split = str(date_init).split(":")[0]
		if date_split != str(self.date):
			frappe.throw("La date de saisie " + str(self.date) + " doit être conforme à la date d'initialisation " + date_split)
	
	def before_submit(self):
		total = 0.00
		for details in self.details_operation_de_caisse :
			total += float(details.montant_devise_ref)

		if float(total) != float(self.montant_reference):
			frappe.throw("Le montant saisie en entête de l'opération " + str(self.montant_reference) + " est différent du total des montants en détails " + str(total) )

		if self.type_caisse == 'Caisse' :
			init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
			if self.type_operation != "Encaissement" :
				if float(init_doc.solde_final) < float(self.montant) :
						frappe.throw("Le montant actuellement en caisse ne permet pas de faire cette opération.\n Il faut augmenter le solde!!!")

		self.generate_journal_entry()

	def on_submit(self):
		init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
		if self.type_operation == "Encaissement" :
			init_doc.solde_final += float(self.montant_reference)
		else:
			init_doc.solde_final -= float(self.montant_reference)
		init_doc.save()
		

	def on_cancel(self):
		init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
		if self.type_operation == "Encaissement" :
			init_doc.solde_final -= float(self.montant_reference)
		else:
			init_doc.solde_final += float(self.montant_reference)
		init_doc.save()
		self.comptabilisation.clear()

	def create_row(self, type, account, cours, amount, type_tiers=None, tiers=None, cc1=None, cc2=None, cc3=None, cc4=None, cc5=None):
		row = {}
		if type == 'Encaissement':
			row = {
				"account": account,
				"exchange_rate": cours,
				#"reference_type": self.doctype,
				#"reference_name": self.name,
				"debit_in_account_currency": amount,
			}
		else:
			row = {
				"account": account,
				"exchange_rate": cours,
				#"reference_type": self.doctype,
				#"reference_name": self.name,
				"credit_in_account_currency": amount,
			}

		if tiers:
			row.update(
				{
					"party_type": "Employee" if type_tiers == "Employe" else ("Customer"if type_tiers == "Client" else "Supplier"),
					"party": tiers,
				}
			)

		if cc1:
			row.update(
				{
					"imputation_analytique": cc1,
				}
			)
		if cc2:
			row.update(
				{
					"imputation_analytique_2": cc2,
				}
			)
		if cc3:
			row.update(
				{
					"imputation_analytique_3": cc3,
				}
			)
		if cc4:
			row.update(
				{
					"imputation_analytique_4": cc4,
				}
			)
		if cc5:
			row.update(
				{
					"imputation_analytique_5": cc5,
				}
			)				

		return row
	

	def create_row2(self, type, compte, cours, montant, tiers=None, cc1=None, cc2=None, cc3=None, cc4=None, cc5=None):
		row = {
				"compte": compte,
				"cours": cours,
				"montant": montant,
				"sens": 'Debit' if type == 'Encaissement' else 'Credit'
			}
		
		
		
		if tiers:
			type_tiers = frappe.db.get_value("Tiers", tiers, "type")
			row.update(
				{
					"type": type_tiers,
					"tiers": tiers,
				}
			)

		if cc1:
			row.update(
				{
					"compte_analytique": cc1,
				}
			)
		if cc2:
			row.update(
				{
					"compte_analytique_2": cc2,
				}
			)
		if cc3:
			row.update(
				{
					"compte_analytique_3": cc3,
				}
			)
		if cc4:
			row.update(
				{
					"compte_analytique_4": cc4,
				}
			)
		if cc5:
			row.update(
				{
					"compte_analytique_5": cc5,
				}
			)

		#frappe.msgprint(str(row))				

		return frappe._dict(row)
	
	def get_account(self, doctype, docname, champ):
		code = frappe.db.get_value(doctype,docname,champ)
		id = frappe.db.get_list("Account",fields=['name'],filters={"account_number": code}) 
		return id[0].name

	def make_accrual_jv_entry(self):
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		journal_entry.user_remark = _("Journal de la caisse {0} pour la journée de {1}").format(self.caisse, self.date)
		journal_entry.company = self.societe #todo
		journal_entry.posting_date = getdate()
		journal_entry.cheque_no = self.name
		journal_entry.cheque_no = self.date
		accounts = []
		currencies = []
		payable_amount = 0
		payable_amt2 = 0
		multi_currency = 0
		company_currency = frappe.db.get_value("Societe",self.societe,"devise_de_base") 
		#acc = self.get_account("Caisse",self.caisse,"compte_comptable")
		#frappe.msgprint(acc)
		caisse_account = self.get_account("Caisse",self.caisse,"compte_comptable")
		cours = flt(get_cours(self.devise, company_currency))

		if self.type_operation == 'Encaissement':
			amount = flt(self.montant_reference, precision)
			payable_amount += amount
			accounting_entry = self.create_row('Encaissement',caisse_account,cours,amount)
			accounts.append(accounting_entry)

			for e in self.details_operation_de_caisse:
				amount = flt(self.montant_reference, precision)
				payable_amount -= amount
				account = self.get_account("Nature Operations",e.nature_operations,"compte_comptable")
				tiers = e.tiers
				cc1 = e.imputation_analytique
				cc2 = e.imputation_analytique_2
				cc3 = e.imputation_analytique_3
				cc4 = e.imputation_analytique_4
				cc5 = e.imputation_analytique_5
				accounting_entry = self.create_row('Decaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5)
				accounts.append(accounting_entry)
		else :
			amount = flt(self.montant_reference, precision)
			payable_amount -= amount
			accounting_entry = self.create_row('Decaissement',caisse_account,cours,amount)
			accounts.append(accounting_entry)

			for e in self.details_operation_de_caisse:
				amount = flt(self.montant_reference, precision)
				payable_amount += amount
				account = self.get_account("Nature Operations",e.nature_operations,"compte_comptable")
				tiers = e.tiers
				cc1 = e.imputation_analytique
				cc2 = e.imputation_analytique_2
				cc3 = e.imputation_analytique_3
				cc4 = e.imputation_analytique_4
				cc5 = e.imputation_analytique_5
				accounting_entry = self.create_row('Encaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5)
				accounts.append(accounting_entry)

		if flt(payable_amount, precision) != 0 :
			#frappe.msgprint(str(payable_amt - payable_amt2))
			round_off_account = self.get_account("Company", self.company,"round_off_account")
			accounting_entry = self.create_row('Decaissement',round_off_account,cours,payable_amount)
			accounts.append(journal_entry)
		
		journal_entry.set("accounts", accounts)
		#frappe.msgprint(str(accounts))
		if len(currencies) > 1:
			multi_currency = 1
		journal_entry.multi_currency = multi_currency
		journal_entry.title = caisse_account
		journal_entry.submit()
	
	def generate_journal_entry(self):
		company_currency = frappe.db.get_value("Societe",self.societe,"devise_de_base") 
		caisse_account = frappe.db.get_value("Caisse",self.caisse,"compte_comptable")
		cours = flt(get_cours(self.devise, company_currency))
		payable_amount = 0

		if self.type_operation == 'Encaissement':
			amount = flt(self.montant_reference, 2)
			payable_amount += amount
			accounting_entry = self.create_row2('Encaissement',caisse_account,cours,amount)
			#self.comptabilisation.append(accounting_entry)
			self.append('comptabilisation', accounting_entry)

			for e in self.details_operation_de_caisse:
				amount = flt(e.montant_devise_ref, 2)
				payable_amount -= amount
				account = frappe.db.get_value("Nature Operations",e.nature_operations,"compte_comptable")
				tiers = e.tiers
				cc1 = e.imputation_analytique
				cc2 = e.imputation_analytique_2
				cc3 = e.imputation_analytique_3
				cc4 = e.imputation_analytique_4
				cc5 = e.imputation_analytique_5
				accounting_entry = self.create_row2('Decaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5)
				self.append('comptabilisation', accounting_entry)
		else :
			amount = flt(self.montant_reference, 2)
			payable_amount -= amount
			accounting_entry = self.create_row2('Decaissement',caisse_account,cours,amount)
			self.append('comptabilisation', accounting_entry)

			for e in self.details_operation_de_caisse:
				amount = flt(e.montant_devise_ref, 2)
				payable_amount += amount
				#frappe.msgprint(str(e.imputation_analytique))
				account = frappe.db.get_value("Nature Operations",e.nature_operations,"compte_comptable")
				tiers = e.tiers
				cc1 = e.imputation_analytique
				cc2 = e.imputation_analytique_2
				cc3 = e.imputation_analytique_3
				cc4 = e.imputation_analytique_4
				cc5 = e.imputation_analytique_5
				accounting_entry = self.create_row2('Encaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5)
				self.append('comptabilisation', accounting_entry)
		
		#frappe.msgprint(str(self.comptabilisation))

		if flt(payable_amount, 2) != 0 :
			compte__arrondi = frappe.db.get_value("Societe",self.societe,"compte__arrondi")
			accounting_entry = self.create_row2('Decaissement',compte__arrondi,cours,payable_amount)
			self.append('comptabilisation', accounting_entry)

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

@frappe.whitelist()
def insert_operation(doc, type= 1):
	aDict = json.loads(doc)
	arg = frappe._dict({
		'doctype': 'Operation de Caisse',
		'code_operation': aDict['name'],
		'initialisation': aDict['initialisation'],
		'type_operation': aDict['type_operation'],
		'designation': aDict['designation'],
		'montant': aDict['montant'],
		'montant_reference': aDict['montant_reference'],
		'devise': aDict['devise'],
		'cours': aDict['cours'],
		'remettant': aDict['remettant'],
		'a_justifier' : aDict['a_justifier'],
	})

	if aDict.get('entite'):
		arg.update({'entite': aDict['entite']})

	if aDict.get('reference'):
		arg.update({'reference': aDict['reference']})

	if aDict.get('commentaire'):
		arg.update({'commentaire': aDict['commentaire']})

	details = []
	for d in aDict['details_operation_de_caisse']:
		arg_sub = frappe._dict({
			'nature_operations': d['nature_operations'],
			'montant_devise': d['montant_devise'],
			'montant_devise_ref': d['montant_devise'],
		})
		if d.get('tiers'):
			arg_sub.update({'tiers': d['tiers']})
		if d.get('imputation_analytique'):
			arg_sub.update({'imputation_analytique': d['imputation_analytique']})
		if d.get('imputation_analytique_2'):
			arg_sub.update({'imputation_analytique_2': d['imputation_analytique_2']})
		if d.get('imputation_analytique_3'):
			arg_sub.update({'imputation_analytique_3': d['imputation_analytique_3']})
		if d.get('imputation_analytique_4'):
			arg_sub.update({'imputation_analytique_4': d['imputation_analytique_4']})
		if d.get('imputation_analytique_5'):
			arg_sub.update({'imputation_analytique_5': d['imputation_analytique_5']})

		details.append(arg_sub)

	arg.update({'details_operation_de_caisse': details})
	#frappe.throw(str(arg))
	if type == 1 :
		frappe.get_doc(arg).insert()
	else :
		frappe.get_doc(arg).save()
	frappe.db.commit()

