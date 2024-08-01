# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils import flt
import json
from treso.trésorerie.doctype.devise.devise import get_cours
from erpnext.setup.utils import get_exchange_rate

class Encaissement(Document):
	def validate(self):
		self.date = frappe.utils.getdate(self.date)
		self.validate_nature()

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

		#if self.type_caisse == 'Caisse' :
		#	init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
		#	if float(init_doc.solde_final) < float(self.montant) :
		#			frappe.throw("Le montant actuellement en caisse ne permet pas de faire cette opération.\n Il faut augmenter le solde!!!")

		self.generate_journal_entry()
		if(self.comptabilite_erpnext == 1):
			self.make_accrual_jv_entry()

	def on_submit(self):
		init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
		init_doc.solde_final += float(self.montant_reference)
		init_doc.save()
		#frappe.db.sql(
		#	"""
		#		UPDATE tabCaisse c 
		#		INNER JOIN tabEncaissement e ON c.name = e.caisse
		#		SET c.solde = c.solde + e.montant, c.date_solde = e.date
		#		WHERE c.name = %(caisse)s AND e.name = %(name)s
		#	""",{"caisse": self.caisse, "name": self.name}, as_dict = 1
		#)

	def on_cancel(self):
		init_doc = frappe.get_doc("Caisse Initialisation", self.initialisation)
		#if init_doc.docstatus == 0:
		init_doc.solde_final -= float(self.montant_reference)
		init_doc.save()

		self.comptabilisation.clear()

		if(self.comptabilite_erpnext == 1):
			nb = frappe.db.count("Journal Entry",  {"cheque_no" : self.name})
			if nb > 0:
				jv = frappe.get_doc("Journal Entry", {"cheque_no" : self.name})
				jv.cancel()

	def create_row(self, type, account, cours, amount, type_tiers=None, tiers=None, cc1=None, cc2=None, cc3=None, cc4=None, cc5=None, cc6=None, cc7=None, cc8=None, cc9=None, cc10=None):
		row = {}
		company_currency = frappe.db.get_value("Societe",self.societe,"devise_de_base") 
		#devise_compte = self.get_account("Account",account,"account_currency")
		ex_rate = flt(get_cours(self.devise, company_currency)[0].cours)

		if type == 'Encaissement':
			row = {
				"account": account,
				"exchange_rate": ex_rate,
				#"reference_type": self.doctype,
				#"reference_name": self.name,
				"debit_in_account_currency": flt(amount * cours, 2),
				"reference_currency": self.devise,
				"reference_rate": cours,
				"reference_amount": amount,
			}
		else:
			row = {
				"account": account,
				"exchange_rate": ex_rate,
				#"reference_type": self.doctype,
				#"reference_name": self.name,
				"credit_in_account_currency": flt(amount * cours, 2),
				"reference_currency": self.devise,
				"reference_rate": cours,
				"reference_amount": amount,
			}

		if tiers:
			if not type_tiers :
				frappe.throw(_("Veuillez renseigner le type tiers du tiers {}").format(tiers))

			row.update(
				{
					"party_type": "Employee" if type_tiers == "Employe" else ("Customer"if type_tiers == "Client" else "Supplier"),
					"party": tiers,
				}
			)

		main = frappe.db.get_value('Cost Center',  {'name': ['like', '%Main%'],'company': self.societe}, 'name')
		if main :
			row.update(
				{
					'cost_center': main,
				}
			)

		if cc1:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 1'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc1,
				}
			)
		if cc2:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 2'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc2,
				}
			)
		if cc3:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 3'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc3,
				}
			)
		if cc4:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 4'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc4,
				}
			)
		if cc5:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 5'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc5,
				}
			)

		if cc6:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 6'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc6,
				}
			)
		if cc7:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 7'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc7,
				}
			)

		if cc8:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 8'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc8,
				}
			)
		if cc9:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 9'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc9,
				}
			)
		if cc10:
			correspondance = frappe.db.get_value('Axe Analytique',  {'type': 'Axe 10'}, 'correspondance')
			analytique = frappe.db.sql(
				'''
					SELECT fieldname
					FROM tabDocField
					WHERE parent = 'Journal Entry Account' and label = %(correspondance)s
					UNION
					SELECT fieldname
					FROM `tabCustom Field`
					WHERE dt = 'Journal Entry Account' and label = %(correspondance)s
				''', {'correspondance': correspondance}, as_dict = 1
			)
			if len(analytique) == 0 :
				frappe.throw(_("La nature analytique {} n'a pas de correspondance dans les dimensions comptables").format(analytique))
			row.update(
				{
					analytique[0].fieldname: cc10,
				}
			)			

		return row
	

	def create_row2(self, type, compte, cours, montant, tiers=None, cc1=None, cc2=None, cc3=None, cc4=None, cc5=None, cc6=None, cc7=None, cc8=None, cc9=None, cc10=None):
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

		if cc6:
			row.update(
				{
					"compte_analytique_6": cc6,
				}
			)
		if cc7:
			row.update(
				{
					"compte_analytique_7": cc7,
				}
			)
		if cc8:
			row.update(
				{
					"compte_analytique_8": cc8,
				}
			)
		if cc9:
			row.update(
				{
					"compte_analytique_9": cc9,
				}
			)
		if cc10:
			row.update(
				{
					"compte_analytique_10": cc10,
				}
			)

		#frappe.msgprint(str(row))				

		return frappe._dict(row)
	
	def get_account(self, doctype, docname, champ):
		code = frappe.db.get_value(doctype,docname,champ)
		#id = frappe.db.get_list("Account",fields=['name'],filters={"account_number": code}) 
		return code
	
	def make_accrual_jv_entry(self):
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		if self.commentaire : 
			journal_entry.user_remark = self.commentaire
		else :
			journal_entry.user_remark = _("Journal de la caisse {0} pour la journée de {1}").format(self.caisse, self.date)
		journal_entry.company = self.societe #todo
		journal_entry.posting_date = self.date
		journal_entry.cheque_no = self.name
		journal_entry.cheque_date = self.date
		accounts = []
		currencies = set()
		payable_amount = 0
		multi_currency = 0
		company_currency = frappe.db.get_value("Societe",self.societe,"devise_de_base") 
		currencies.add(company_currency)
		caisse_account = self.get_account("Caisse",self.caisse,"compte_comptable")
		account_currency = self.get_account("Account",caisse_account,"account_currency")
		cours = flt(get_cours(self.devise, account_currency)[0].cours)
		currencies.add(self.devise)

		amount = flt(self.montant_reference, precision)
		payable_amount += amount
		accounting_entry = self.create_row('Encaissement',caisse_account,cours,amount)		
		accounts.append(accounting_entry)

		for e in self.details_operation_de_caisse:
			amount = flt(e.montant_devise, precision)
			payable_amount -= amount
			account = self.get_account("Nature Operations",e.nature_operations,"compte_comptable")
			devise = self.get_account("Account",account,"account_currency")
			cours = flt(get_cours(self.devise, devise)[0].cours)
			currencies.add(devise)
			
			tiers = e.tiers
			cc1 = e.imputation_analytique
			cc2 = e.imputation_analytique_2
			cc3 = e.imputation_analytique_3
			cc4 = e.imputation_analytique_4
			cc5 = e.imputation_analytique_5

			cc6 = e.imputation_analytique_6
			cc7 = e.imputation_analytique_7
			cc8 = e.imputation_analytique_8
			cc9 = e.imputation_analytique_9
			cc10 = e.imputation_analytique_10
			accounting_entry = self.create_row('Decaissement',account,cours,amount,e.type_tiers,tiers,cc1,cc2,cc3,cc4,cc5,cc6,cc7,cc8,cc9,cc10)
			accounts.append(accounting_entry)

		if flt(payable_amount, precision) != 0 :
			round_off_account = self.get_account("Company", self.societe,"round_off_account")
			devise = self.get_account("Account",account,"round_off_account")
			cours = flt(get_cours(self.devise, devise)[0].cours)
			accounting_entry = self.create_row('Decaissement',round_off_account,cours,payable_amount)
			accounts.append(journal_entry)
		
		if len(currencies) > 1:
			multi_currency = 1
			
		journal_entry.multi_currency = multi_currency
		journal_entry.title = caisse_account
		journal_entry.set("accounts", accounts)
		#frappe.throw(str(accounts))
		journal_entry.submit()

	def generate_journal_entry(self):
		company_currency = frappe.db.get_value("Societe",self.societe,"devise_de_base") 
		caisse_account = frappe.db.get_value("Caisse",self.caisse,"compte_comptable")
		cours = get_cours(self.devise, company_currency)[0].cours
		payable_amount = 0

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

			cc6 = e.imputation_analytique_6
			cc7 = e.imputation_analytique_7
			cc8 = e.imputation_analytique_8
			cc9 = e.imputation_analytique_9
			cc10 = e.imputation_analytique_10
			accounting_entry = self.create_row2('Decaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5,cc6,cc7,cc8,cc9,cc10)
			#accounting_entry = self.create_row2('Decaissement',account,cours,amount,tiers,cc1,cc2,cc3,cc4,cc5)
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



