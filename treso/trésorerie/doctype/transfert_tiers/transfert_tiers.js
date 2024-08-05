// Copyright (c) 2024, Ebama Dernis and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transfert Tiers", {
    refresh: function(frm) {

        $('.primary-action').prop('hidden', true);

        frm.add_custom_button(__('Transférer'), function() {
            if (!frm.doc.societe || frm.doc.societe.trim() === '') {
                frappe.throw({
                    title: __('Erreur'),
                    indicator: 'red',
                    message: __('Le champ Société est requis.')
                });
            } else {
                let fiend = 0;
                let promises = []; // Tableau pour stocker les promesses
        
                frm.doc.table.forEach(function(item) {
                    let promise = new Promise((resolve) => {
                        frappe.call({
                            method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                            args: {
                                code: item.code
                            },
                            callback: function(response) {
                                const data = response.message;
                                if (data && data.length > 0) {
                                    data.forEach(function(row) {
                                        console.log(`Code: ${row.code}`);
                                    });
                                    resolve(); // Résoudre la promesse
                                } else {
                                    let doctype = "Tiers";
                                    let tiers = frappe.model.get_new_doc(doctype);
        
                                    tiers.code = item.code;
                                    tiers.type = item.type;
                                    tiers.intitule = item.intitule;
                                    tiers.email = item.email;
                                    tiers.collectif = item.collectif;
                                    tiers.telephone = item.telephone;
                                    tiers.societe = frm.doc.societe;  
                                    tiers.adresse = item.adresse;
        
                                    frappe.db.insert(tiers).then(function(doc) {
                                        if (doc) {
                                            fiend++;
                                            console.log(`Code: ${fiend}`);
                                        }
                                        resolve(); // Résoudre la promesse après l'insertion
                                    });
                                }
                            },
                            error: function(err) {
                                console.error('Erreur lors de la récupération des codes:', err);
                                frappe.msgprint(__('Erreur: ', [err]));
                                resolve(); // Résoudre la promesse même en cas d'erreur
                            }
                        });
                    });
        
                    promises.push(promise); // Ajouter la promesse au tableau
                });
        
                // Attendre que toutes les promesses soient résolues
                Promise.all(promises).then(function() {
                    if (fiend > 0) {
                        if (fiend >= 2) {
                            console.log(`Yes: ${fiend}`);
                            frappe.msgprint(__(`${fiend} tiers enregistrés`));
                        } else {
                            frappe.msgprint(__(`${fiend} tier enregistré`));
                            console.log(`No: ${fiend}`);
                        }
                    }
                });
            }
        }).addClass('btn btn-primary text-white');
        
        let myButton = $("button[data-fieldname='recharger']");

        myButton.css({
            "background-color": "#000",
            "color": "#fff",
            "border-color": "#000",
            "position": "relative",
            "padding-right": "20px" 
        });

        myButton.css("&:after", {
            "content": "'\u25B6'", 
            "font-size": "12px",
            "color": "#fff", 
            "position": "absolute",
            "top": "50%",
            "right": "10px",
            "transform": "translateY(-50%)"
        });
        
        const allowed_doc_types = ['Employee', 'Customer', 'Supplier', 'Patient','Student']; // Remplacez par vos DocTypes souhaités

        // Filtrer les options du champ Link
        frm.fields_dict['type_doc'].get_query = function() {
            return {
                filters: [
                    ['name', 'in', allowed_doc_types]
                ]
            };
        };

        if (frm.doc.mode_transfert === 'Individuel') {
            
            frm.fields_dict.table.df.hidden = 1;
            frm.fields_dict.recharger.df.hidden = 1;
            frm.fields_dict.tiers.df.hidden = 0;
        } else {

            frm.fields_dict.table.df.hidden = 0;
            frm.fields_dict.recharger.df.hidden = 0;
            frm.fields_dict.tiers.df.hidden = 1;

        }
        // Rafraîchir le formulaire pour appliquer les changements
        frm.refresh_field('table');
        frm.refresh_field('recharger');
        frm.refresh_field('type_doc');
        frm.refresh_field('tiers');

    },
    
    mode_transfert: function(frm) {
        // Vérifier la valeur du champ de condition
        if (frm.doc.mode_transfert === 'Individuel') {
            
            frm.doc.table = []; 
            frm.refresh_field('table');

            frm.fields_dict.table.df.hidden = 1;
            frm.fields_dict.recharger.df.hidden = 1;
            frm.fields_dict.tiers.df.hidden = 0;
        } else {

            frm.fields_dict.table.df.hidden = 0;
            frm.fields_dict.recharger.df.hidden = 0;
            frm.fields_dict.tiers.df.hidden = 1;

            frm.doc.table = []; 
            frm.refresh_field('table');

        }
        // Rafraîchir le formulaire pour appliquer les changements
        frm.refresh_field('table');
        frm.refresh_field('recharger');
        frm.refresh_field('type_doc');
        frm.refresh_field('tiers');
    },
    
    fieldname: function(frm) {
        frm.page.set_primary_action('Transférer', () => {
            frm.save().then(() => {
                frappe.msgprint(__('Enregistrement effectué avec succès'));
            });
        });
    },
    recharger: function(frm) {
        if (!frm.doc.societe) return;
        frm.clear_table('table');
        let my_socite = frm.selected_doc.societe;
        let type_doc = frm.selected_doc.type_doc;

        

        if ( type_doc === 'Customer' ) {
            frappe.call({
                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_customers_transferts",
                args: {
                    'my_socite': my_socite
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        console.log(type_doc);
                        r.message.forEach(function(item) {
                            console.log(type_doc);
                            frappe.call({
                                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                                args: {
                                    code: item.name
                                },
                                callback: function(response) {
                                    const data = response.message;
                                    if (data && data.length > 0) {
                                        data.forEach(function(row) {
                                            console.log(`Code: ${row.code}`);
                                        });
                                        resolve(); 
                                    } else {
                                                                                
                                        frm.add_child('table', {
                                            'code': item.name,
                                            'type': 'CLIENT',
                                            'intitule': item.name,
                                            'email': item.email,
                                            'collectif': item.account,
                                            'societe': item.company
                                        });
                                        
                                    }
                                },
                                error: function(err) {
                                    console.error('Erreur lors de la récupération des codes:', err);
                                    frappe.msgprint(__('Erreur: ', [err]));
                                    resolve(); 
                                }
                            });
                            
                        });
                        frm.refresh_field('table');
                        frm.refresh();
                    }
                }
            });
        }
        if ( type_doc === 'Employee' ) {
            frappe.call({
                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_Employee_transferts",
                args: {
                    'my_socite': my_socite
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        r.message.forEach(function(item) {

                            frappe.call({
                                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                                args: {
                                    code: item.employee
                                },
                                callback: function(response) {
                                    const data = response.message;
                                    if (data && data.length > 0) {
                                        data.forEach(function(row) {
                                            console.log(`Code: ${row.code}`);
                                        });
                                        resolve(); 
                                    } else {
                                        
                                        frm.add_child('table', {
                                            'code': item.employee,
                                            'type': 'SALARIE',
                                            'intitule': item.employee_name,
                                            'email': item.personal_email,
                                            'collectif': item.default_employee_account,
                                            'telephone' : item.employee_number,
                                            'societe': item.company,
                                            'adresse' : item.current_address
                                        });

                                    }
                                },
                                error: function(err) {
                                    console.error('Erreur lors de la récupération des codes:', err);
                                    frappe.msgprint(__('Erreur: ', [err]));
                                    resolve(); 
                                }
                            });

                        });
                        frm.refresh_field('table');
                        frm.refresh();
                    }
                }
            });
        }

        if ( type_doc === 'Student' ) {
            frappe.call({
                
                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_Student_transferts",
                args: {
                    'my_socite': my_socite
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        r.message.forEach(function(item) {

                            frappe.call({
                                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                                args: {
                                    code: item.name
                                },
                                callback: function(response) {
                                    const data = response.message;
                                    if (data && data.length > 0) {
                                        data.forEach(function(row) {
                                            console.log(`Code: ${row.code}`);
                                        });
                                        resolve(); 
                                    } else {
                                                                                
                                        console.log(item.name);
                                        console.log(item.student_name);
                                        console.log(item.student_email_id);
                                        frm.add_child('table', {
                                            'code': item.name,
                                            'type': 'ETUDIANT',
                                            'intitule': item.student_name,
                                            'email': item.student_email_id,
                                            'collectif': item.default_student_account,
                                            'telephone' : item.student_mobile_number,
                                            'societe': item.company_name,
                                            'adresse' : item.address_line_1
                                        });
                                        
                                    }
                                },
                                error: function(err) {
                                    console.error('Erreur lors de la récupération des codes:', err);
                                    frappe.msgprint(__('Erreur: ', [err]));
                                    resolve(); 
                                }
                            });
                            
                        });
                        frm.refresh_field('table');
                        frm.refresh();
                    }
                }
            });
        }
        
        if ( type_doc === 'Supplier' ) {
            frappe.call({
                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_Supliers_transferts",
                args: {
                    'my_socite': my_socite
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        r.message.forEach(function(item) {

                            frappe.call({
                                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                                args: {
                                    code: item.supplier_name
                                },
                                callback: function(response) {
                                    const data = response.message;
                                    if (data && data.length > 0) {
                                        data.forEach(function(row) {
                                            console.log(`Code: ${row.code}`);
                                        });
                                        resolve(); 
                                    } else {
                                        
                                        frm.add_child('table', {
                                            'code': item.supplier_name,
                                            'type': 'FOURNISSEUR',
                                            'intitule': item.supplier_name,
                                            'email': item.email_id,
                                            'collectif': item.default_supplier_account,
                                            'telephone' : item.phone,
                                            'societe': item.company_name,
                                            'adresse' : item.address_line1
                                        });
                                        
                                    }
                                },
                                error: function(err) {
                                    console.error('Erreur lors de la récupération des codes:', err);
                                    frappe.msgprint(__('Erreur: ', [err]));
                                    resolve(); 
                                }
                            });
                            
                        });
                        frm.refresh_field('table');
                        frm.refresh();
                    }
                }
            });
        }

        if ( type_doc === 'Patient' ) {
            frappe.call({
                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_Patients_transferts",
                args: {
                    'my_socite': my_socite
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        r.message.forEach(function(item) {

                            frappe.call({
                                method: "treso.trésorerie.doctype.transfert_tiers.tier_sent.get_tiers_code",
                                args: {
                                    code: item.name
                                },
                                callback: function(response) {
                                    const data = response.message;
                                    if (data && data.length > 0) {
                                        data.forEach(function(row) {
                                            console.log(`Code: ${row.code}`);
                                        });
                                        resolve(); 
                                    } else {
                                        
                                        frm.add_child('table', {
                                            'code': item.name,
                                            'type': 'PATIENT',
                                            'intitule': item.name,
                                            'email': item.email,
                                            'collectif': item.default_patient_account,
                                            'telephone' : item.mobile,
                                            'societe': item.company_name                               
                                        });
                                        
                                    }
                                },
                                error: function(err) {
                                    console.error('Erreur lors de la récupération des codes:', err);
                                    frappe.msgprint(__('Erreur: ', [err]));
                                    resolve(); 
                                }
                            });
                            
                        });
                        frm.refresh_field('table');
                        frm.refresh();
                    }
                }
            });
        }
        
    }
    
});
