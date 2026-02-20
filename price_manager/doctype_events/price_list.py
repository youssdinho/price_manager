import frappe

MARGE_DEFAUT = 10.0

@frappe.whitelist()
def propager_sur_tous_les_articles(price_list_name):
    price_list = frappe.get_doc("Price List", price_list_name)
    pl_marge_defaut = price_list.get("marge_defaut") or MARGE_DEFAUT

    items = frappe.get_all("Item", filters={"disabled": 0}, fields=["name"])
    count_created = 0
    count_updated = 0

    for item in items:
        item_code = item["name"]

        result = frappe.db.sql("""
            SELECT SUM(actual_qty * valuation_rate) / NULLIF(SUM(actual_qty), 0)
            FROM `tabBin`
            WHERE item_code = %s
        """, item_code)

        valuation_rate = result[0][0] if result and result[0][0] else None
        pmp_ttc = (valuation_rate * 1.20) if valuation_rate and valuation_rate > 0 else 0

        existing = frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": price_list_name},
            ["name", "marge"],
            as_dict=True
        )

        if existing:
            count_updated += 1
        else:
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": price_list_name,
                "price_list_rate": round(pmp_ttc * (1 + pl_marge_defaut / 100), 2) if pmp_ttc else 0,
                "marge": pl_marge_defaut
            }).insert(ignore_permissions=True)
            count_created += 1

    frappe.db.commit()
    return {"created": count_created, "updated": count_updated}

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
