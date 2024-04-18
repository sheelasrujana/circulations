from odoo import fields, api, models


class StockReturnPickingDetails(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_details = fields.One2many('return.details', 'stock_return_picking')


class ReturnDetails(models.TransientModel):
    _name = 'return.details'

    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Return Location')
    stock_return_picking = fields.Many2one('stock.return.picking')
