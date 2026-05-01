app_name = "price_manager"
app_title = "Price Manager"
app_publisher = "erpuser"
app_description = "Gestion automatique des prix de vente"
app_email = "erpuser@amanatem.local"
app_license = "mit"

scheduler_events = {
	"cron": {
		"0 3 * * *": [
			"price_manager.doctype_events.scheduled.update_all_prices"
		]
	}
}

doc_events = {
	"Purchase Invoice": {
		"on_submit": "price_manager.doctype_events.purchase_invoice.on_submit"
	},
	"Item": {
		"after_insert": "price_manager.doctype_events.item.after_insert"
	},
	"Price List": {
		"after_insert": "price_manager.doctype_events.price_list.after_insert",
		"on_trash": "price_manager.doctype_events.price_list.on_trash"
	}
}

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "in", ["Price List", "Item Price"]],
			["fieldname", "in", ["marge_defaut", "marge"]]
		]
	}
]

doctype_js = {
	"Price List": "public/js/price_list.js",
	"Item": "public/js/item.js"
}
