import frappe

TVA = 1.20
MARGE_DEFAUT = 10.0

def on_submit(doc, method):
    selling_price_lists = frappe.get_all(
        "Price List",
        filters={"selling": 1, "enabled": 1},
        fields=["name", "marge_defaut"]
    )

    if not selling_price_lists:
        return

    for item_line in doc.items:
        item_code = item_line.item_code

        result = frappe.db.sql("""
            SELECT SUM(actual_qty * valuation_rate) / NULLIF(SUM(actual_qty), 0)
            FROM `tabBin`
            WHERE item_code = %s
        """, item_code)

        valuation_rate = result[0][0] if result and result[0][0] else None

        if not valuation_rate or valuation_rate <= 0:
            frappe.log_error(f"PMP introuvable pour {item_code}", "Price Manager")
            continue

        pmp_ttc = valuation_rate * TVA

        for price_list in selling_price_lists:
            pl_name = price_list["name"]
            pl_marge_defaut = price_list.get("marge_defaut") or MARGE_DEFAUT

            existing = frappe.db.get_value(
                "Item Price",
                {"item_code": item_code, "price_list": pl_name},
                ["name", "marge"],
                as_dict=True
            )

            if existing:
                marge = existing.get("marge")
                if not marge or marge == 0:
                    marge = pl_marge_defaut
                prix_vente = pmp_ttc * (1 + marge / 100)
                frappe.db.set_value("Item Price", existing["name"], "price_list_rate", round(prix_vente, 2))
            else:
                marge = pl_marge_defaut
                prix_vente = pmp_ttc * (1 + marge / 100)
                frappe.get_doc({
                    "doctype": "Item Price",
                    "item_code": item_code,
                    "price_list": pl_name,
                    "price_list_rate": round(prix_vente, 2),
                    "marge": marge,
                    "valid_from": "2000-01-01"
                }).insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.msgprint("Prix de vente mis à jour avec succès.", alert=True)
