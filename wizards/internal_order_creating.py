from odoo import api, models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class InternalOrderCreating(models.Model):
    _name = 'internal.order.creating'

    def create_internal_order(self):
        printing_units = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        for units in printing_units:
            if units.servie_regions:
                product = self.env['product.product'].search(
                    [('unit_id', '=', units.id), ('is_newspaper', '=', True)])
                if product:
                    internal_order = []
                    partner_id = self.env['res.partner'].search([('name', '=', 'USHODAYA ENTERPRISES PRIVATE LIMITED')])
                    internal_order_vals = {
                        'partner_id': partner_id.id,
                        'internal_order': True
                    }
                    internal_order.append(self.env['sale.order'].create(internal_order_vals))
                    for rec in internal_order:
                        product_line_vals = {
                            'partner_id': units.id,
                            'newspaper_date': fields.Datetime.now() + timedelta(days=1),
                            'product_id': product.id,
                            'order_id': rec.id,
                        }
                        rec.add_new_product.create(product_line_vals).adding_zone_from_addition()
                        rec.lines_added()

    def create_internal_order_for_unit(self):
        current_user = self.env.user.id
        printing_units = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        for units in printing_units:
            if units.user_id.id == current_user:
                if units.servie_regions:
                    product = self.env['product.product'].search(
                        [('unit_id', '=', units.id), ('is_newspaper', '=', True)])
                    if product:
                        internal_order = []
                        partner_id = self.env['res.partner'].search(
                            [('name', '=', 'USHODAYA ENTERPRISES PRIVATE LIMITED')])
                        internal_order_vals = {
                            'partner_id': partner_id.id,
                            'internal_order': True
                        }
                        internal_order.append(self.env['sale.order'].create(internal_order_vals))
                        for rec in internal_order:
                            product_line_vals = {
                                'partner_id': units.id,
                                'newspaper_date': fields.Datetime.now() + timedelta(days=1),
                                'product_id': product.id,
                                'order_id': rec.id,
                            }
                            rec.add_new_product.create(product_line_vals).adding_zone_from_addition()
                            rec.lines_added()

