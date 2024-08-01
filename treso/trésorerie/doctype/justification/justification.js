// Copyright (c) 2024, Ebama Dernis and contributors
// For license information, please see license.txt

frappe.ui.form.on('Justification', {
	setup: function(frm) {
		frm.set_query("operation", function() {
			return {
				"filters": {
					"docstatus": 1,
					"justifie": 0,
				}
			};
		});
		frm.set_query("nature_operations","details_operation_de_caisse", function() {
			return {
				"filters": {
					"type_operation": 'Décaissement',
				}
			};
		});
	},
	// refresh: function(frm) {

	// }
});
