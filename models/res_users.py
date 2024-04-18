import re
import logging
from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import UserError


class ResUsersCustom(models.Model):
    _description = "Agents Create"
    _inherit = 'res.users'

    is_agent = fields.Boolean('Is agent?')
    is_newsprint_unit = fields.Boolean('Is NewsPrint Unit?')
    sale_order_line_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Sale Line Document Access')
    account_move_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Account Document Access')
    account_payment_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Payment Document Access')
    demand_request_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Demand Request Document Access')

    return_request_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Return Request Document Access')

    deposit_history_document_access = fields.Selection([
        ('own', 'Own Document'),
        ('all', 'All Document'),
        ('admin', 'Administrator')
    ], string='Deposit History Document Access')

    hr_employee_circulation_agent = fields.Many2one('hr.employee', )

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsersCustom, self).create(vals_list)

        if users.is_agent:
            users.partner_id.is_newsprint_agent = True
            users.partner_id.active_agent = True
            users.partner_id.user_id = users.id
        else:
            if users.is_newsprint_unit:
                users.partner_id.is_printing_unit = True
                users.partner_id.user_id = users.id

        return users

    def action_server_sales_circulation_payment_view(self):
        # Retrieve the date parameter from the context (you can pass it from the action)
        user = self.env.uid
        # Parse the date string into a date object
        today = fields.Date.today()
        user_id = self.env['res.users'].browse(user)
        unit_payment_ids = self.env['res.partner'].search([('is_printing_unit', '=', True),
                                                           ('user_id', '=', user_id.id)])
        # This loop for to search the circulation units agents payments
        circulation_head__payment_unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        unit_agent_ids = []
        head_agent_ids = []

        # Loop for unit agents
        if unit_payment_ids:
            for unit in unit_payment_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                unit_agent_ids.append(agents.cc_zone.id)
        # Find the sale order record based on the given date
        domain = [('partner', 'in', unit_agent_ids)]
        return {
            'name': _('Agents Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': domain,
            'views_id': False,
            'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                      (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

        }

    def _get_vendor_domain(self):
        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        for obj in self:
            agent_ids = []
            for line in user_id.partner_id.servie_regions.district_o2m.zone_o2m.add_zones_to_line.cc_zone:
                for vendor_id in line.vendor_id.ids:
                    agent_ids.append(vendor_id)
                self.vendor_list = [(6, 0, agent_ids)]
        print(self.vendor_list, 'ndsoijfiaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

    vendor = fields.Many2one('res.partner', string="Vendor")
    vendor_list = fields.Many2many('res.partner', store=True, compute=_get_vendor_domain)



