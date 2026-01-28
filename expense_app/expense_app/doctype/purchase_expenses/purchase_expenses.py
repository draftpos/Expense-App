# Copyright (c) 2026, Munyaradzi Chirove and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class PurchaseExpenses(Document):
    def before_save(self):
        total_amount = 0
        for d in self.items:
            d.total = d.qty * d.rate
            total_amount += d.total

        self.subtotal = total_amount

    def on_submit(self):
        self.create_purchase_invoice()

        # If marked as paid, create Payment Entry
        if self.is_paid:
            self.create_payment_entry()

    def create_purchase_invoice(self):
        """
        Automatically create a Purchase Invoice when a Purchase Expense is submitted
        """
        # Prevent duplicate invoices
        if frappe.db.exists("Purchase Invoice", {"purchase_expense": self.name}):
            return

        items = []
        for d in self.items:
            items.append({
                "item_code": d.item_name,  # map your item field
                "qty": d.qty,
                "rate": d.rate,
                "amount": d.total
            })

        invoice = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": self.supplier,
            "posting_date": nowdate(),
            "items": items,
            "purchase_expense": self.name,  # link back to the expense
            "company": self.company
        })

        invoice.insert()
        invoice.submit()  # auto-submit invoice
        frappe.db.commit()

        # Store invoice name on this Purchase Expense
        self.purchase_invoice = invoice.name
        return

    def create_payment_entry(self):
        """
        Create a Payment Entry for the linked Purchase Invoice
        """
        if not self.purchase_invoice:
            frappe.throw("Purchase Invoice not found. Cannot create Payment Entry.")

        # Prevent duplicate Payment Entries
        if frappe.db.exists("Payment Entry", {"reference_name": self.purchase_invoice}):
            return

        invoice = frappe.get_doc("Purchase Invoice", self.purchase_invoice)

        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": invoice.supplier,
            "paid_to": invoice.company,  # or Bank/Cash account
            "paid_amount": invoice.total,
            "received_amount": invoice.total,
            "reference_no": invoice.name,
            "reference_date": invoice.posting_date,
            "reference_name": invoice.name,
            "company": invoice.company
        })

        payment_entry.insert()
        payment_entry.submit()
        frappe.db.commit()

        # Store Payment Entry name on this Purchase Expense
        self.payment_entry = payment_entry.name
