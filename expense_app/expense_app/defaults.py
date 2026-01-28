import frappe
def install_defaults():
    from .create_default_items import insert_items
    from .create_default_supplier import insert_suppliers
    insert_items()
    insert_suppliers()
    frappe.msgprint("Default payroll items, suppliers, accounts, and salary components have been installed.")