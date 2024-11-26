import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, get_datetime
from datetime import datetime
import requests

@frappe.whitelist()
def get_invoice_items(start, end, pos_warehouse, user):
    data = frappe.db.sql("""
        SELECT
            sii.item_code, sii.item_name, SUM(sii.qty) as total_quantity
        FROM
            `tabSales Invoice Item` sii
        INNER JOIN
            `tabSales Invoice` si ON sii.parent = si.name
        WHERE
            si.owner = %s
            AND si.docstatus = 1
            AND sii.warehouse = %s
            AND sii.creation BETWEEN %s AND %s 
        GROUP BY
            sii.item_code, sii.item_name
    """, (user, pos_warehouse, start, end), as_dict=True)

    print(data)
    return data


@frappe.whitelist()
def get_invoice_items_for_print():
    data = frappe.db.sql("""
        SELECT
            sii.item_code, sii.item_name, SUM(sii.qty) as total_quantity
        FROM
            `tabSales Invoice Item` sii
        INNER JOIN
            `tabSales Invoice` si ON sii.parent = si.name
        LIMIT 1
    """)
    print(data)
    return data

# @frappe.whitelist()
# def send_salary_slips(entry_no):
#     payroll_entry = frappe.get_doc('Payroll Entry', entry_no)

#     # Possible earnings and deductions (you might want to fetch these from a settings doctype)
#     all_earnings = ["Basic Salary", "Fuel Allowance", "Arrear", "Overtime", "Bonus", "Commission", "Misc"]
#     all_deductions = ["Advance Salary", "Loan against salary", "Deduction for leaves", "EOBI", "P Fund", "Income Tax", "Other Deductions"]

#     if payroll_entry and hasattr(payroll_entry, 'employees'):
#         for employee in payroll_entry.employees:
#             email = employee.email_for_salary_slip
#             if not email:
#                 continue

#             salary_slip = frappe.get_doc('Salary Slip', {'payroll_entry': entry_no, 'employee': employee.employee})

#             # Initialize earnings and deductions dictionaries with zeros
#             earnings_dict = {earning: 0 for earning in all_earnings}
#             deductions_dict = {deduction: 0 for deduction in all_deductions}

#             # Fill in the actual values from the salary slip
#             for earning in salary_slip.earnings:
#                 earnings_dict[earning.salary_component] = earning.amount
#             for deduction in salary_slip.deductions:
#                 deductions_dict[deduction.salary_component] = deduction.amount

#             # Construct the email body with earnings and deductions
#             email_body = f"<h3>Salary Details for {employee.employee_name}</h3>"
#             email_body += "<h4>Earnings:</h4>"
#             email_body += "<table border='1'><tr><th>Description</th><th>Amount</th></tr>"
            
#             for desc, amount in earnings_dict.items():
#                 email_body += f"<tr><td>{desc}</td><td>{amount}</td></tr>"
            
#             email_body += "</table><br><h4>Deductions:</h4>"
#             email_body += "<table border='1'><tr><th>Description</th><th>Amount</th></tr>"
            
#             for desc, amount in deductions_dict.items():
#                 email_body += f"<tr><td>{desc}</td><td>{amount}</td></tr>"
            
#             email_body += "</table>"

#             # Sending the email
#             subject = _("Salary Slip Details for {0}").format(employee.employee_name)
#             frappe.sendmail(recipients=email, subject=subject, message=email_body, delayed=False)

#     frappe.msgprint(_("Salary slips sent to all employees for payroll entry {0}.").format(entry_no))

    # frappe.msgprint(_("Salary slips sent to all employees for payroll entry {0}.").format(entry_no))

# Commenting this temporarily to push code on live
# @frappe.whitelist()
# def send_salary_slips(entry_no):
#     payroll_entry = frappe.get_doc('Payroll Entry', entry_no)
#     template_path = frappe.get_app_path('vapesd_customizations', 'templates', 'pages', 'salary_slip.html')

#     all_earnings = ["Basic Salary", "Fuel Allowance", "Arrear", "Overtime", "Bonus", "Commission", "Misc"]
#     all_deductions = ["Advance Salary", "Loan against salary", "Deduction for leaves", "EOBI", "P Fund", "Income Tax","Pick and Drop", "Audit", "Food Allowance", 
#                      "Cleaning", "Late Arrival", "Fine", "Other Deductions"]

#     try:
#         template = frappe.read_file(template_path)
#     except Exception as e:
#         frappe.throw(_("Failed to load template: {0}".format(str(e))))

#     if payroll_entry and hasattr(payroll_entry, 'employees'):
#         for employee in payroll_entry.employees:
#             email = employee.email_for_salary_slip
#             if not email:
#                 continue

#             salary_slip = frappe.get_doc('Salary Slip', {'payroll_entry': entry_no, 'employee': employee.employee})

#             earnings_dict = {earning.salary_component: earning.amount for earning in salary_slip.earnings}
#             deductions_dict = {deduction.salary_component: deduction.amount for deduction in salary_slip.deductions}
#             gross_salary  = salary_slip.gross_pay
#             total_deductions  = salary_slip.total_deduction
#             net_salary  = salary_slip.net_pay
#             payslip_date = salary_slip.start_date.strftime('%B-%Y')
            
#             email_body = frappe.render_template(template, {
#                 'employee_name': employee.employee_name,
#                 'earnings': earnings_dict,
#                 'deductions': deductions_dict,
#                 'all_earnings': all_earnings,
#                 'all_deductions': all_deductions,
#                 'gross_salary': gross_salary,
#                 'total_deductions': total_deductions,
#                 'net_salary': net_salary,
#                 'for_the_month_of': payslip_date,
#             })

#             subject = _("Salary Slip Details for {0}").format(employee.employee_name)
#             frappe.sendmail(recipients=email, subject=subject, message=email_body, delayed=False)

#     frappe.msgprint(_("Salary slips sent to all employees for payroll entry {0}.").format(entry_no))


@frappe.whitelist()
def send_invoice_to_php_api(doc, method):
    if doc.pos_profile:
        # Get the POS Profile record using frappe.get_doc()
        pos_profile = frappe.get_doc('POS Profile', doc.pos_profile)
        
        # Access the required fields from the POS Profile
        switch_fbr_on = pos_profile.switch_fbr_on
        fbr_pos_id = pos_profile.fbr_pos_id
        ntn_no = pos_profile.ntn_no
        fbr_branch_token = pos_profile.branch_token
        jurisdiction = pos_profile.jurisdiction
        gst_rate = pos_profile.gst_rate
        tunnel_url = pos_profile.tunnel_url
    
    if not pos_profile.switch_fbr_on:
        frappe.log("No need to report invoice.")
        return
    
    if not doc.payments:
        frappe.throw(_("No payments found in the Sales Invoice."))

    # Get the first payment's mode_of_payment from the child table
    first_payment_mode = doc.payments[0].mode_of_payment if doc.payments else None

    if not first_payment_mode:
        frappe.throw(_("No payment mode found in the first payment."))

    # get the following things from POS Profile of doc.pos_profile
    # ntn_no
    # jurisdiction
    # fbr_pos_id
    # fbr_branch_token
    # gst_rate
    
    
    # then add them in the invoice data
    
    # Prepare the data in the correct format
    invoice_data = {
        "ntn_no": ntn_no,
        "erp_invoice_no": doc.name,  # Adjust this based on your logic
        "total_bill_amount": doc.grand_total,
        "total_sales_value": doc.net_total,
        "total_qty": sum([item.qty for item in doc.items]),
        "gross_total_amount": sum([item.amount for item in doc.items]),
        "total_vat": 0,
        "total_discount": doc.discount_amount or 0,
        "payment_mode": first_payment_mode,
        "fbrItems": [
            {
                "ItemCode": item.item_code,
                "ItemName": item.item_name,
                'PCTCode' : 21069090,
                "Quantity": item.qty,
                "TaxRate" : gst_rate,
                "SaleValue": round(item.rate * item.qty,2),
                "TaxCharged": round(item.qty * item.rate * 0.18,2),
                "TotalAmount": round(item.qty * item.rate * 1.18,2),
                "InvoiceType": 1
            } for item in doc.items
        ],
        "jurisdiction": jurisdiction,
        "pos_profile": doc.pos_profile,
        "pos_shift": doc.posa_pos_opening_shift,
        "fbr_pos_id": fbr_pos_id,
        "fbr_branch_token": fbr_branch_token,
        "gst_rate": gst_rate,
        "tunnel_url": tunnel_url,
        'switch_fbr_on': switch_fbr_on
    }

    # Send the request to the Laravel API running at http://192.168.100.45:8002/api/send-to-fbr
    response = requests.post("http://192.168.100.70:8002/api/send-to-fbr", json=invoice_data)

    # Check if the request was successful
    if response.status_code == 200:
        # Log the success without showing a message to the user
        frappe.log(f"Invoice {doc.name} sent to FBR successfully.", "FBR API Success")
    else:
            frappe.log_error(f"FBR API Error: {response.text}", "FBR API")
            frappe.throw(_("Failed to send invoice to FBR. Please check the logs."))