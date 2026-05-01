import frappe

MARGE_DEFAUT = 10.0

def after_insert(doc, method):
    selling_price_lists = frappe.get_all(
        "Price List",
        filters={"selling": 1, "enabled": 1},
        fields=["name", "marge_defaut"]
    )

    for price_list in selling_price_lists:
        pl_name = price_list["name"]
        pl_marge_defaut = price_list.get("marge_defaut") or MARGE_DEFAUT

        ip = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": doc.name,
            "price_list": pl_name,
            "price_list_rate": 0,
            "marge": pl_marge_defaut,
            "valid_from": "2000-01-01"
        })
        ip.flags.ignore_permissions = True
        ip.flags.ignore_mandatory = True
        ip.flags.ignore_links = True
        ip.flags.print_after_save = False
        ip.insert()

    frappe.db.commit()
