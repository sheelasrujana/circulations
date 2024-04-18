from odoo import models, fields


class ProductSchedular(models.Model):
    _inherit = 'product.product'

    def on_hand_function_mrp(self):
        product_id = self.env['product.product'].search([('is_newspaper', '=', True)])
        for product in product_id:
            # ('location_id', '!=', product.scrap_location.id),
            if product.scrap_location:
                print(product.bom_ids.picking_type_id.default_location_dest_id.name)
                stock_quant = self.env['stock.quant'].search(
                    [('product_id', '=', product.id),
                     ('location_id', '=', product.bom_ids.picking_type_id.default_location_dest_id.id)])
                for stock in stock_quant:
                    # print(stock.quantity)
                    # print(stock.lot_id.name)
                    if stock.quantity > 0:
                        self.env['stock.quant'].create({
                            'location_id': product.scrap_location.id,
                            'quantity': stock.quantity,
                            'product_id': product.id,
                            'lot_id': stock.lot_id.id,
                        })
                        stock.quantity = 0
