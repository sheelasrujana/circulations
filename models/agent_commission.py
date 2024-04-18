from odoo import fields, api, models, _
from datetime import date, timedelta


class Agent_Sales(models.Model):
    _inherit = 'sale.order.line'

    agent_cr_id = fields.Many2one('agent.credit')


class AgentCredit(models.Model):
    _name = 'agent.credit'
    _rec_name = 'agent_id'
    _description = 'Credit Notes for Agent-Free Copies'

    agent_id = fields.Many2one('res.partner', string='Agent')
    line_ids = fields.One2many('sale.order.line', 'agent_cr_id', string='Order Lines')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    unit_price = fields.Float('Unit Price')
    total_copies = fields.Integer('No of Copies')
    total_amount = fields.Float('Total Amount')
    status = fields.Selection([('draft', 'Draft'),
                                       ('waiting', 'Waiting For Approvals'),
                                       ('approved', 'Approved'),
                                       ('cr', 'CR Done'),
                                       ('cancel', 'Canceled'),
                                       ])

    def get_sale_orders(self):
        if self.agent_id:
            sale_order_lines = self.env['sale.order.line'].search([
                ('create_date', '>=', self.start_date),
                ('create_date', '<=', self.end_date),
                ('free_copies', '>', 0),
            ])
            sale_order_lines.write({'agent_cr_id': self.id})
            self.write({'status': 'waiting'})
            total_copies = 0
            if sale_order_lines:
                for rec in sale_order_lines:
                    total_copies = rec.free_copies
                self.total_copies = total_copies
                self.unit_price = 0.50
                self.total_copies = (self.unit_price * total_copies)

    def send_for_approvals(self):
        self.write({'status': 'approved'})

    def cancel_cr_notes(self):
        self.write({'status': 'cancel'})

    def create_credit_note(self):
        self.write({'status': 'cr'})
        product_id = self.env['product.product'].search([('name','=','Credit Notes for Agent-Free Copies')], limit=1)
        if not product_id:
            product_id = self.env['product.product'].create({
                'name': 'Credit Notes for Agent-Free Copies',
                'list_price': 0.50,
                'detailed_type': 'service',
                'taxes_id': False,
                    })
            product_id.write({'l10n_in_hsn_code': product_id.id})
        move_id = self.env['account.move'].create({
            'partner_id': self.agent_id.id,
            'unit_id': self.agent_id.unit.id,
            'l10n_in_state_id': self.agent_id.state_id.id,
            'invoice_date': date.today(),
            'move_type': 'out_refund'
        })
        move_line_id = self.env['account.move.line'].create({
            'move_id': move_id.id,
            'product_id': product_id.id,
            'quantity': self.total_copies,
            'currency_id': self.env.company.currency_id.id,
            'display_type': 'product',
        })
