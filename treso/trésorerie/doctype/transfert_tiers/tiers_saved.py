import frappe

@frappe.whitelist()
def get_customers_transferts_individuel(my_socite,tiers):
    return frappe.db.sql(
        """
        SELECT
        P.company AS company,
        P.account AS account,
        C.name AS name,
        C.primary_address AS primary_address
        FROM `tabCustomer` C
        LEFT JOIN `tabParty Account` P
        ON P.parent = C.name
        WHERE P.company = %(my_socite)s AND C.name = %(tiers)s 
        """, 
        {"my_socite": my_socite, "tiers" : tiers}, 
        as_dict=1
    )


@frappe.whitelist()
def get_Employee_transferts_individuel(my_socite,tiers):
    return frappe.db.sql(
        """
        SELECT
            E.current_address,
            E.employee,
            E.employee_name,
            E.name,
            E.employee_number,
            E.company,
            E.personal_email,
            C.default_employee_account
        FROM `tabEmployee` E
        LEFT JOIN `tabCompany` C ON C.company_name = E.company
        WHERE E.status = 'Active'  AND E.company = %(my_socite)s AND E.employee = %(tiers)s
        """, 
        {"my_socite": my_socite, "tiers" : tiers}, 
        as_dict=1
    )


@frappe.whitelist()
def get_Student_transferts_individuel(my_socite,tiers):
    return frappe.db.sql(
        """
            SELECT
                S.address_line_1,
                S.student_name,
                S.name,
                S.student_mobile_number,
                S.student_email_id,
                P.program,
                C.default_student_account,
                C.company_name

            FROM `tabStudent` S
            CROSS JOIN (
                SELECT C.company_name, C.default_student_account 
                FROM `tabCompany` C 
                WHERE C.company_name = %(my_socite)s  AND S.name = %(tiers)s 
                LIMIT 1
            ) AS C
            LEFT JOIN `tabProgram Enrollment` P ON P.name = S.name;

        """, 
        {"my_socite": my_socite, "tiers" : tiers}, 
        as_dict=1
    )


@frappe.whitelist()
def get_Supliers_transferts_individuel(my_socite,tiers):
    return frappe.db.sql(
        """                   
            SELECT
                S.supplier_name,
                A.phone,
                A.address_title,
                A.address_line1,
                A.email_id,
                C.default_supplier_account,
                C.company_name
            FROM `tabSupplier` S
            CROSS JOIN (
                SELECT C.company_name, C.default_supplier_account 
                FROM `tabCompany` C 
                WHERE C.company_name = %(my_socite)s AND S.supplier_name = %(tiers)s 
            ) AS C
            LEFT JOIN `tabAddress` A ON A.name = S.supplier_primary_address

        """, 
        {"my_socite": my_socite, "tiers" : tiers}, 
        as_dict=1
    )

@frappe.whitelist()
def get_Patients_transferts_individuel(my_socite,tiers):
    return frappe.db.sql(
        """
            
        SELECT
            S.name,
            S.mobile,
            S.email,
            C.default_patient_account,
            C.company_name
        FROM `tabPatient` S
        CROSS JOIN (
        SELECT C.company_name, C.default_patient_account 
        FROM `tabCompany` C 
        WHERE C.company_name = %(my_socite)s AND S.name = %(tiers)s 
        ) AS C
        """, 
        {"my_socite": my_socite, "tiers" : tiers}, 
        as_dict=1
    )
