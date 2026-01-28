import frappe

@frappe.whitelist()
def insert_items():
    items = [
        "General Expense Item" 
    ]

    # dedupe but keep order
    unique_items = list(dict.fromkeys(items))

    for item_name in unique_items:

        if not frappe.db.exists("Item", {"item_code": item_name}):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": item_name,
                "item_name": item_name,
                "item_group": "Services",  
                "stock_uom": "Nos",                
                "is_stock_item": 0
            })
            item.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted → {item_name}")
        else:
            print(f"Skipped (already exists) → {item_name}")
