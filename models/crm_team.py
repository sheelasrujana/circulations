from odoo import fields, api, models


class SaleOrderInvoice(models.Model):
    _inherit = 'crm.team'

    parent_team_id = fields.Many2one('crm.team', string="Parent Team")