import frappe
import time

TVA = 1.20
MARGE_DEFAUT = 10.0
BATCH_SIZE = 500


def update_all_prices():
	start = time.time()

	bins = frappe.db.sql("""
		SELECT item_code, MAX(valuation_rate) as valuation_rate
		FROM `tabBin`
		WHERE valuation_rate > 0
		GROUP BY item_code
	""", as_dict=True)

	item_prices = frappe.db.sql("""
		SELECT ip.name, ip.item_code, ip.price_list, ip.marge
		FROM `tabItem Price` ip
		JOIN `tabPrice List` pl ON pl.name = ip.price_list
		WHERE pl.selling = 1
		AND pl.enabled = 1
		AND ip.docstatus != 2
	""", as_dict=True)

	price_lists = frappe.db.sql("""
		SELECT name, marge_defaut
		FROM `tabPrice List`
		WHERE selling = 1 AND enabled = 1
	""", as_dict=True)

	if not bins or not price_lists:
		frappe.logger("price_manager").info("[Price Manager] Aucun article ou Price List trouvé, job annulé.")
		return

	pmp_map = {b.item_code: b.valuation_rate for b in bins}
	ip_map = {(ip.item_code, ip.price_list): ip for ip in item_prices}
	pl_map = {pl.name: (pl.marge_defaut or MARGE_DEFAUT) for pl in price_lists}

	nb_traites = 0
	nb_mis_a_jour = 0
	nb_crees = 0
	nb_erreurs = 0
	compteur = 0

	for item_code, valuation_rate in pmp_map.items():
		pmp_ttc = valuation_rate * TVA

		for pl_name, marge_defaut in pl_map.items():
			try:
				existing = ip_map.get((item_code, pl_name))

				if existing:
					marge = existing.get("marge")
					if not marge or marge == 0:
						marge = marge_defaut
					prix_vente = round(pmp_ttc * (1 + marge / 100), 2)
					frappe.db.set_value("Item Price", existing["name"], "price_list_rate", prix_vente)
					nb_mis_a_jour += 1
				else:
					marge = marge_defaut
					prix_vente = round(pmp_ttc * (1 + marge / 100), 2)
					frappe.get_doc({
						"doctype": "Item Price",
						"item_code": item_code,
						"price_list": pl_name,
						"price_list_rate": prix_vente,
						"marge": marge,
						"valid_from": "2000-01-01"
					}).insert(ignore_permissions=True)
					nb_crees += 1

			except Exception as e:
				frappe.log_error(f"Erreur prix {item_code} / {pl_name} : {e}", "Price Manager Scheduled")
				nb_erreurs += 1

		nb_traites += 1
		compteur += 1
		if compteur > 0 and compteur % BATCH_SIZE == 0:
			frappe.db.commit()

	frappe.db.commit()

	nb_ignores = len(frappe.db.sql("SELECT DISTINCT item_code FROM `tabBin`")) - len(pmp_map)
	duree = round(time.time() - start)

	frappe.logger("price_manager").info(
		f"[Price Manager] Mise à jour terminée :\n"
		f"- Articles traités : {nb_traites}\n"
		f"- Prix mis à jour  : {nb_mis_a_jour}\n"
		f"- Prix créés       : {nb_crees}\n"
		f"- Articles ignorés : {nb_ignores} (sans PMP)\n"
		f"- Erreurs          : {nb_erreurs}\n"
		f"- Durée            : {duree}s"
	)
