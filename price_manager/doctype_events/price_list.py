import frappe

MARGE_DEFAUT = 10.0

def after_insert(doc, method):
    if not doc.selling:
        return

    pl_marge_defaut = doc.get("marge_defaut") or MARGE_DEFAUT
    items = frappe.get_all("Item", filters={"disabled": 0}, fields=["name"])

    for item in items:
        item_code = item["name"]

        result = frappe.db.sql("""
            SELECT SUM(actual_qty * valuation_rate) / NULLIF(SUM(actual_qty), 0)
            FROM `tabBin`
            WHERE item_code = %s
        """, item_code)

        valuation_rate = result[0][0] if result and result[0][0] else None
        pmp_ttc = (valuation_rate * 1.20) if valuation_rate and valuation_rate > 0 else 0

        frappe.get_doc({
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": doc.name,
            "price_list_rate": round(pmp_ttc * (1 + pl_marge_defaut / 100), 2) if pmp_ttc else 0,
            "marge": pl_marge_defaut
        }).insert(ignore_permissions=True)

    frappe.db.commit()

def on_trash(doc, method):
    if not doc.selling:
        return
    frappe.db.delete("Item Price", {"price_list": doc.name})
    frappe.db.commit()
