from odoo import api, fields, models


class CustomSaleOrderMenu(models.Model):
    _inherit = 'sale.order'

    def create_custom_menu(self):
        quotation_menu = self.env.ref(
            'sale.menu_sale_quotations')  # Assuming the original menu item is 'menu_sale_quotations'

        custom_menu = self.env['ir.ui.menu'].create({
            'name': 'Custom Menu',
            'parent_id': quotation_menu.parent_id.id,
        })
        return custom_menu

    @api.model
    def init(self):
        self.create_custom_menu()

