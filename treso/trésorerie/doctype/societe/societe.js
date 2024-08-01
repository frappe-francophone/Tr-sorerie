// Copyright (c) 2024, Ebama Dernis and contributors
// For license information, please see license.txt


frappe.ui.form.on('Societe', {
	// refresh: function(frm) {

	// }
	billetage: function(frm){
		if(frm.doc.billetage == 1){
			cur_frm.set_value("billetage_operation", 1);
			cur_frm.set_value("billetage_encaissement", 1);
		}
		else{
			cur_frm.set_value("billetage_operation", 0);
			cur_frm.set_value("billetage_encaissement", 0);
		}
	},
	billetage_operation: function(frm){
		//frm.set_value("billetage_encaissement", 1);
	},
	billetage_encaissement: function(frm){
		//frm.set_value("billetage_operation", 0);
	},
	
});
