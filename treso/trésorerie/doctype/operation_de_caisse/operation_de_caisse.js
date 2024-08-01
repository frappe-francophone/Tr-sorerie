// Copyright (c) 2024, Ebama Dernis and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operation de Caisse', {
	setup: function(frm) {
		frm.set_query("initialisation", function() {
			return {
				"filters": {
					//"caisse": frm.doc.caisse || 'N/A', 
					"docstatus": 0
				}
			};
		});

		frm.set_query("nature_operations","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type_operation": frm.doc.type_operation || 'N/A',
				}
			};
		});

		frm.set_query("imputation_analytique","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Section 1',
				}
			};
		});
		frm.set_query("imputation_analytique_2","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Section 2',
				}
			};
		});
		frm.set_query("imputation_analytique_3","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Section 3',
				}
			};
		});
		frm.set_query("imputation_analytique_4","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Section 4',
				}
			};
		});
		frm.set_query("imputation_analytique_5","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Section 5',
				}
			};
		});

		if(frm.doc.type_operation == 'Encaissement') {
			frm.set_value('code_type', 'ENC');
			frm.set_value('remettant', frappe.session.user);
			frm.set_df_property('remettant', 'label', 'Remettant');
		}
		else {
			frm.set_value('code_type', 'DEC');
			frm.set_value('remettant', '');
			frm.set_df_property('remettant', 'label', 'Bénéficiaire');
		}
		if(!frm.is_new() && frm.is_dirty()){
			frm.save();
		}
	},
	refresh: function(frm){
		/*frm.add_custom_button(__("Caisse Quotidienne"),
			function () {
				//frappe.route_options = {"name": frm.doc.initialisation};
				frappe.set_route('Form', 'Caisse Initialisation',{"name": frm.doc.initialisation});
			}
		)*/

		
	},
	
	type_operation: function(frm) {
		if(frm.doc.type_operation == 'Encaissement') {
			frm.set_value('code_type', 'ENC');
			frm.set_value('remettant', frappe.session.user);
			frm.set_df_property('remettant', 'label', 'Remettant');
		}
		else {
			frm.set_value('code_type', 'DEC');
			frm.set_value('remettant', '');
			frm.set_df_property('remettant', 'label', 'Bénéficiaire');
		}
	},
	devise: function(frm) {
		frappe.call({
			method: "ls_treso.ls_treso.doctype.devise.devise.get_cours",
			args: {
				reference: frm.doc.devise_caisse,
				devise: frm.doc.devise,
			},
			callback: function (r) {
				if (r.message) {
                    if(r.message.length > 0) {
						frm.set_value('cours', r.message[0].cours);
						if(frm.doc.montant) frm.set_value('montant_reference', frm.doc.montant / r.message[0].cours);
						//frm.refresh_field('cours'); 
					}
					else{
						frm.set_value('cours', 0);
						frm.set_value('montant_reference', 0);
					}
                }
			}
		});
	},
	montant: function(frm) {
		if(frm.doc.cours) frm.set_value('montant_reference', frm.doc.montant / frm.doc.cours);
	},
});

frappe.ui.form.on('Details Operation de Caisse', {
	
    montant_devise(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        if(row.montant_devise && frm.doc.cours){
			row.montant_devise_ref = row.montant_devise / frm.doc.cours;
		}
		else{
			row.montant_devise_ref = 0;
		}
        frm.refresh_field('montant_devise_ref');
        //frm.refresh_field('total');
        frm.refresh();
    },
	details_operation_de_caisse_add:(frm, cdt, cdn) =>{
		var total = 0;
		var row = locals[cdt][cdn];

		frm.doc.details_operation_de_caisse.forEach(e => {
			total += e.montant_devise ? e.montant_devise : 0;
		});
		
		if (frm.doc.montant){
			if (frm.doc.montant > total){
				row.montant_devise = frm.doc.montant - total;
				row.montant_devise_ref = frm.doc.montant - total;
			}
			else {
				row.montant_devise = 0;
				row.montant_devise_ref = 0;
			}
			frm.refresh_field('montant_devise');
			frm.refresh_field('montant_devise_ref');
			frm.refresh_field('details_operation_de_caisse');
		}
	},
});

