# Copyright (c) 2024, Ebama Dernis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Devise(Document):
	pass

@frappe.whitelist()
def get_billetage(devise):
	return frappe.db.sql(
		"""
			SELECT unite, nom, photo
			FROM `tabBillet`
			WHERE parent = '%s'
			ORDER BY unite, cast(nom AS int)
		""" % (devise), as_dict = 1
	)

@frappe.whitelist()
def get_cours(reference, devise):
	return frappe.db.sql(
		"""
			SELECT v.cours
			FROM
			(
				SELECT d.parent as reference, d.devise, max(d.date_cours) AS date_cours, t.cours
				FROM `tabCours Devise` d INNER JOIN 
					(
						SELECT parent, devise, date_cours, cours
						FROM `tabCours Devise` 
					) AS t ON t.parent = d.parent AND t.devise = d.devise AND t.date_cours = d.date_cours
				GROUP BY d.parent, d.devise
				UNION
				SELECT '%(reference)s' AS reference, '%(reference)s' AS devise, CURDATE() AS date_cours, 1 AS cours
			) v
			WHERE v.reference = '%(reference)s' AND v.devise = '%(devise)s'
		""" % {"reference":reference, "devise":devise}, as_dict = 1
	)
	