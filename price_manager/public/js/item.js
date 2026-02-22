frappe.ui.form.on("Item", {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("item_name", "");
		}
	},
	item_code: function(frm) {
		frm.set_value("item_name", "");
	}
});
