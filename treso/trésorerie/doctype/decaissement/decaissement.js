// Copyright (c) 2024, Ebama Dernis and contributors
// For license information, please see license.txt

frappe.ui.form.on('Decaissement', {
	setup: function(frm) {
		frm.set_query("initialisation", function() {
			return {
				"filters": {
					"docstatus": 0
				}
			};
		});
		

		frm.set_query("nature_operations","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type_operation": frm.doc.type_operation || 'N/A',
					"est_valide": 1,
					//"account_currency": frm.doc.devise_caisse,
				}
			};
		});

		frm.set_query("imputation_analytique","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 1',
				}
			};
		});
		frm.set_query("imputation_analytique_2","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 2',
				}
			};
		});
		frm.set_query("imputation_analytique_3","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 3',
				}
			};
		});
		frm.set_query("imputation_analytique_4","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 4',
				}
			};
		});
		frm.set_query("imputation_analytique_5","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 5',
				}
			};
		});

		frm.set_query("imputation_analytique_6","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 6',
				}
			};
		});
		frm.set_query("imputation_analytique_7","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 7',
				}
			};
		});
		frm.set_query("imputation_analytique_8","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 8',
				}
			};
		});
		frm.set_query("imputation_analytique_9","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 9',
				}
			};
		});
		frm.set_query("imputation_analytique_10","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type": 'Axe 10',
				}
			};
		});

		frm.set_value('type_operation', 'Decaissement');
	},
	refresh(frm) {
		frm.add_custom_button('Demandes de Paiment',() =>{ 
			let query_args = {
				//query:"ls_treso.ls_treso.doctype.decaissement.decaissement.get_demande_paiement",
				filters: { 
					site: cur_frm.doc.site, 
					positione : 0,
					docstatus : 1,
					devise: cur_frm.doc.devise,
				}
			} 
            new frappe.ui.form.MultiSelectDialog({
                doctype: "Demande Paiement",
                target: cur_frm,
                setters: {
					designation: "",
					remettant: "",
					montant: "",
					devise: cur_frm.doc.devise,
                },
                add_filters_group: 1,
				date_field: "date",
                columns: ["name","designation", "remettant","montant","devise"],
                get_query() {
                    return query_args;
                },
                action(selections, args) { //details_operation_de_caisse
                    console.log("params");
					if(selections.length == 1){
						frappe.db.get_doc("Demande Paiement",selections[0]).then(d =>{
							cur_frm.doc.designation = d.designation;
							cur_frm.doc.montant = d.montant;
							cur_frm.doc.montant_reference = d.montant;
							cur_frm.doc.entite = d.entite;
							cur_frm.doc.reference = d.reference;
							cur_frm.doc.remettant = d.remettant;

							d.details_operation_de_caisse.forEach(e => {
								var row = cur_frm.add_child('details_operation_de_caisse');
								row.nature_operations = e.nature_operations;
								row.montant_devise = e.montant_devise;
								row.montant_devise_ref = e.montant_devise;
								row.demande_paiement = d.name;
								if(e.tiers) row.tiers = e.tiers;
								if(e.imputation_analytique) row.imputation_analytique = e.imputation_analytique;
								if(e.imputation_analytique_2) row.imputation_analytique_2 = e.imputation_analytique_2;
								if(e.imputation_analytique_3) row.imputation_analytique_3 = e.imputation_analytique_3;
								if(e.imputation_analytique_4) row.imputation_analytique_4 = e.imputation_analytique_4;
								if(e.imputation_analytique_5) row.imputation_analytique_5 = e.imputation_analytique_5;

								if(e.imputation_analytique_6) row.imputation_analytique_6 = e.imputation_analytique_6;
								if(e.imputation_analytique_7) row.imputation_analytique_7 = e.imputation_analytique_7;
								if(e.imputation_analytique_8) row.imputation_analytique_8 = e.imputation_analytique_8;
								if(e.imputation_analytique_9) row.imputation_analytique_9 = e.imputation_analytique_9;
								if(e.imputation_analytique_10) row.imputation_analytique_10 = e.imputation_analytique_10;
							});
							cur_frm.dirty();
							cur_frm.refresh();
						});
					}
					else if(selections.length > 1) {
						selections.forEach(s => {
							console.log(selections);
							cur_frm.doc.commentaire = "";
							cur_frm.doc.montant = 0;
							frappe.db.get_doc("Demande Paiement",s).then(d =>{
								cur_frm.doc.commentaire += d.designation + " " + d.montant + " " + d.devise + " " + d.reference + " " + d.remettant + "\n";
								d.details_operation_de_caisse.forEach(e => {
									var row = cur_frm.add_child('details_operation_de_caisse');
									row.nature_operations = e.nature_operations;
									row.montant_devise = e.montant_devise;
									cur_frm.doc.montant += e.montant_devise;
									row.demande_paiement = d.name;
									if(e.tiers) row.tiers = e.tiers;
									if(e.imputation_analytique) row.imputation_analytique = e.imputation_analytique;
									if(e.imputation_analytique_2) row.imputation_analytique_2 = e.imputation_analytique_2;
									if(e.imputation_analytique_3) row.imputation_analytique_3 = e.imputation_analytique_3;
									if(e.imputation_analytique_4) row.imputation_analytique_4 = e.imputation_analytique_4;
									if(e.imputation_analytique_5) row.imputation_analytique_5 = e.imputation_analytique_5;

									if(e.imputation_analytique_6) row.imputation_analytique_6 = e.imputation_analytique_6;
									if(e.imputation_analytique_7) row.imputation_analytique_7 = e.imputation_analytique_7;
									if(e.imputation_analytique_8) row.imputation_analytique_8 = e.imputation_analytique_8;
									if(e.imputation_analytique_9) row.imputation_analytique_9 = e.imputation_analytique_9;
									if(e.imputation_analytique_10) row.imputation_analytique_10 = e.imputation_analytique_10;
								});
								cur_frm.dirty();
								cur_frm.refresh();
							});
						});

					}
                    
					
                },
                //allow_child_item_selection: true,
                //child_fieldname: "availability_details",
                //child_columns: ["description","day","start_time","end_time"] // retorune name dans args.filtered_children   
            });
        },);
		/*if(frm.doc.docstatus === 1){
			frm.page.btn_primary.hide();
			frm.page.btn_secondary.hide();
			frm.page.clear_primary_action();
			
		}
		frappe.db.get_doc("Caisse Initialisation", cur_frm.doc.initialisation).then(d => {
			if(d.docstatus === 1){
				frm.page.btn_primary.hide();
				frm.page.btn_secondary.hide();
				frm.page.clear_primary_action();

				var span;
				var a;
				var li;
				span = document.querySelector('[data-label="New%20Decaissement"]');
				if(span){
					a = span.parentElement;
					li = a.parentElement;
					li.style.display = "None";
				}
				span = document.querySelector('[data-label="Duplicate"]');
				if(span){
					a = span.parentElement;
					li = a.parentElement;
					li.style.display = "None";
				}
				span = document.querySelector('[data-label="Rename"]');
				if(span){
					a = span.parentElement;
					li = a.parentElement;
					li.style.display = "None";
				}
			}
			if(d.docstatus === 0){
				if(frm.is_new()){
					if(frm.doc.initialisation == ""){
						frm.set_value('initialisation', d.name);
					}
				}
			}
		});*/
		if (!frm.customFlag){
			var grid = frm.get_field('details_operation_de_caisse');
			// Add a new empty row to the grid
			grid.grid.add_new_row();
			frm.customFlag = true;
		}
		

	},
	devise: function(frm) {
		if(!frm.doc.devise_caisse) return;
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
	/*after_insert: function(frm){
		if(! frm.is_new()) return;
		frappe.set_route("Form", "Operation de Caisse", frm.doc.name);
	},
	/*after_save: function(frm){
		if(frm.is_new()) return;
		frappe.call({
			method: "ls_treso.ls_treso.doctype.operation_de_caisse.operation_de_caisse.insert_operation",
			args: {
				doc: frm.doc,
				type: 2,
			},
			callback: function (r) {
				frappe.set_route("Form", "Operation de Caisse", frm.doc.name);
			}
		});
	},
	
	before_insert: function(frm){
		frm.doc.details_operation_de_caisse.forEach(e => {
			frappe.db.get_value("Nature Operations", e.nature_operations, "justifiable", (r) => {
				if(r.justifiable == 'Oui'){
					if(!e.imputation_analytique) frappe.throw("Ligne " + e.idx +  ": Veuillez renseigner la nature analytique");
				}
			});
			
			frappe.db.get_value("Nature Operations", e.nature_operations, "tiers", (r) => {
				if(r.tiers == 'Oui'){
					if(!e.tiers) frappe.throw("Ligne " + e.idx +  ": Veuillez renseigner le tiers");
				}
			});
		});
	},
	before_save: function(frm){
		frm.doc.details_operation_de_caisse.forEach(e => {
			frappe.db.get_value("Nature Operations", e.nature_operations, "justifiable", (r) => {
				if(r.justifiable == 'Oui'){
					if(!e.imputation_analytique) frappe.throw("Ligne " + e.idx +  ": Veuillez renseigner la nature analytique");
				}
			});
			
			frappe.db.get_value("Nature Operations", e.nature_operations, "tiers", (r) => {
				if(r.tiers == 'Oui'){
					if(!e.tiers) frappe.throw("Ligne " + e.idx +  ": Veuillez renseigner le tiers");
				}
			});
		});
	},*/
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

		if (row.demande_paiement) frm.call("update_demande", row.demande_paiement, "add");
	},
	details_operation_de_caisse_remove:(frm, cdt, cdn) =>{
		var row = locals[cdt][cdn];
		if (row.demande_paiement) frm.call("update_demande", row.demande_paiement, "remove");
	},
});

frappe.ui.form.on("Decaissement","refresh", function(frm, cdt, cdn) { 
	var df_axe_1 = frappe.meta.get_docfield("Details Operation de Caisse","imputation_analytique", cur_frm.doc.name);
	frappe.db.get_value("Axe Analytique", {"type": "Axe 1"}, "name").then(r=>{
		df_axe_1.label = r.message.name;
		div = document.querySelector('[data-fieldname="imputation_analytique"]');
		div.children[1].innerText = r.message.name;
	});
	/*df = frappe.meta.get_docfield("Details Operation de Caisse","imputation_analytique_2", cur_frm.doc.name);
    df.read_only = 1;
	df = frappe.meta.get_docfield("Details Operation de Caisse","imputation_analytique_3", cur_frm.doc.name);
    df.read_only = 1;
    var df = frappe.meta.get_docfield("Details Operation de Caisse","imputation_analytique_4", cur_frm.doc.name);
    df.read_only = 1;
	df = frappe.meta.get_docfield("Details Operation de Caisse","imputation_analytique_5", cur_frm.doc.name);
    df.read_only = 1;
	//df.hidden = 1;
	df = frappe.meta.get_docfield("Details Operation de Caisse","reste", cur_frm.doc.name);
    df.read_only = 1;
	//df.hidden = 1; */

});
