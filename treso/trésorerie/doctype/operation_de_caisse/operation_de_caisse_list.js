frappe.listview_settings['Operation de Caisse'] = {

    onload: function (listview) {

        /*// Add a button for doing something useful.
        listview.page.add_inner_button(__("Décaissement"), function () {
                        frappe.new_doc("Decaissement", true);  // change to your function's name
        }).addClass("btn-warning")
          .css({'background-color':'#2490EF','color':'white','font-weight': 'normal'});
        
        // Add a button for doing something useful.
        listview.page.add_inner_button(__("Encaissement"), function () {
            frappe.new_doc("Encaissement", true);  // change to your function's name
        }).addClass("btn-warning")
          .css({'background-color':'#2490EF','color':'white','font-weight': 'normal'});
        */
        // Run custom code when the ListView is loaded
        // Use event delegation to handle click events on ListView items
    },
    refresh: function (listview){
        listview.page.btn_primary.hide();
        listview.page.btn_secondary.hide();
        /*listview.data.forEach(function(list_item) {
            list_item.route = "";
            var docname = list_item.name;
            var custom_route = 'app/encaissement/' + docname;
            if(docname.includes("DEC")) custom_route = 'app/decaissement/' + docname;
            // Update the route field of the item
            list_item.route = custom_route;
        });*/

        /*listview.$result.on('click', 'a.list-row', function() {
            // Get the docname of the clicked item
            var docname = $(this).attr('data-name');
            // Set the custom route for the item
            var custom_route = 'app/encaissement/' + docname;
            if(docname.includes("DEC")) custom_route = 'app/decaissement/' + docname;
            // Use frappe.set_route() to navigate to the custom route
            frappe.set_route(custom_route);
        });*/

        listview.data.forEach(function(list_item) {
            // Get the DocType name and docname of each item
            var doctype = list_item.doctype;
            var docname = list_item.name;
            var docname1 = $(this).attr('data-name');
            // Set the custom route for each item
            var custom_route = 'app/encaissement/' + docname;
            if(docname.includes("DEC")) custom_route = 'app/decaissement/' + docname;
            // Update the route field of the item
            list_item.route = custom_route;
            // Add a click event listener to each item
            list_item.$el.on('click', function() {
                // Use frappe.set_route() to navigate to the custom route
                frappe.set_route(custom_route);
            });
        });
    }
};