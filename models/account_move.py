from odoo import fields, api, models, _
from datetime import datetime, timedelta

import datetime


class SaleOrderInvoice(models.Model):
    _inherit = 'sale.order'

    def action_view_invoice(self):
        res = super(SaleOrderInvoice, self).action_view_invoice()
        invoices = self.mapped('invoice_ids')
        for invoice in invoices:
            if invoice.invoice_origin.startswith('IO') and invoice.invoice_origin == self.name:
                invoice.write({'internal_order_bool': True})
        return res


class AccountMoveBool(models.Model):
    _inherit = 'account.move'

    is_transportation = fields.Boolean('Is Transportation')
    is_not_circulation_head = fields.Boolean('Is Not Circulation Head')
    internal_order_bool = fields.Boolean('Is Internal order')
    return_request_bool = fields.Boolean('Is Return Request?')
    total = fields.Float('Total Copies')
    newsprint_agent = fields.Many2one('res.partner', 'Newsprint Agent')
    return_id = fields.Many2one('return.request', 'Return ID')
    ret_ids = fields.Many2many('stock.picking', string='New')
    unit_id = fields.Many2one('res.partner', domain=[('is_printing_unit', '=', True)])
    transportation_unit_id = fields.Many2one('res.partner', domain=[('is_printing_unit', '=', True)])
    payment_status = fields.Selection([
        ('on_time', 'Paid on Time'),
        ('late', 'Paid Late'),
    ], compute='_compute_payment_status', string='Payment Status', store=True)
    payment_details = fields.One2many('payment.informations.invoice', 'payment_details')

    @api.depends('payment_state', 'invoice_date_due', 'invoice_date')
    def _compute_payment_status(self):
        for invoice in self:
            if invoice.payment_state == 'in_payment' or invoice.payment_state == 'partial':
                if invoice.invoice_date_due and invoice.invoice_date:
                    # Calculate the number of days overdue
                    current_date = datetime.datetime.now().date()
                    overdue_days = (invoice.invoice_date_due - current_date).days
                    if abs(overdue_days) <= 10:
                        invoice.payment_status = 'on_time'
                    else:
                        invoice.payment_status = 'late'
                else:
                    invoice.payment_status = False
            else:
                invoice.payment_status = False

    def action_create_invoice_count_per_fiscal_year_and_customer(self):
        for agent in self.env['res.partner'].search([('is_newsprint_agent', '=', True)]):
            current_month = datetime.datetime.now().month
            on_time_payment = 0
            late_payment = 0
            inv_obj = self.env['account.move'].search([('partner_id', '=', agent.id),
                                                        ('move_type', '=', 'out_invoice'),
                                                        ('state', '!=', 'draft'),
                                                        ('state', '!=', 'cancel')], limit=current_month)
            for invoice in inv_obj:
                if invoice.payment_status == 'on_time':
                    on_time_payment += 1
                elif invoice.payment_status == 'late':
                    late_payment += 1
                else:
                    on_time_payment = on_time_payment
                    late_payment = late_payment
            agent_inv_count = len(inv_obj)
            percentage_payment_status = 0
            if agent_inv_count !=0:
                percentage_payment_status = on_time_payment/agent_inv_count * 100
            if percentage_payment_status >= 33.34:
                agent.deposit_interest = 8
            else:
                agent.deposit_interest = 4

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.account_move_document_access == 'own':
            args += [('partner_id', '=', self.env.user.partner_id.id)]
        # elif self.env.user.sale_order_line_document_access == 'all':
        #     if self.env.user.has_group('base.group_erp_manager'):
        #         return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order,
        #                                                         count=count)
        #     else:
        #         user_groups = self.env.user.groups_id.ids
        #         args += ['|', ('user_id', '=', self.env.user.id), ('user_id', 'in', user_groups)]
        return super(AccountMoveBool, self).search(args, offset=offset, limit=limit, order=order, count=count)

    def action_post(self):
        agent_report_credit = self.env['account.move'].search(
            [('internal_order_bool', '=', True), ('return_request_bool', '=', True)])
        for agent_report in agent_report_credit:
            return_request = self.env['return.request'].search([('id', '=', agent_report.return_id.id)])
            if return_request:
                for lines in return_request.return_request_line:
                    lines.is_credit_done = True
                    lines.state = 'credit_note_done'
        return super(AccountMoveBool, self).action_post()

    # This Is For Invoice Of Particular Agents(Schedule Action also)
    def creating_agent_invoices(self):
        current_date = fields.Date.today()
        one_month_ago = current_date - timedelta(days=30)
        sale_orders = self.env['sale.order'].search([('internal_order', '=', True),
                                                     ('create_date', '>=', one_month_ago),
                                                     ('create_date', '<=', current_date)])
        agent_list = []
        product_list = []
        for order in sale_orders:
            for line in order.order_line:
                if line.region_s:
                    if line.region_s.id not in agent_list:
                        agent_list.append(line.region_s.id)
                    if line.product_id.id not in product_list:
                        product_list.append(line.product_id.id)

        for agent_id in agent_list:
            total_copies = 0
            invoice_line_list = []
            for product in product_list:
                agent_obj = self.env['res.partner'].browse(agent_id)
                product_obj = self.env['product.product'].browse(product)
                so_line_obj = self.env['sale.order.line'].search(
                    [('product_id', '=', product), ('region_s', '=', agent_id)])
                for so_line in so_line_obj:
                    total_copies += so_line.product_uom_qty - agent_obj.f_q_zone + agent_obj.p_q_zone + agent_obj.v_q_zone + agent_obj.pr_q_zone + agent_obj.c_c_zone + agent_obj.o_q_zone
                    so_ids = self.env['sale.order'].search([('order_line', '=', so_line.id)])
                invoice_line = {
                    'product_id': product_obj.id,
                    'quantity': total_copies,
                    'price_unit': product_obj.lst_price,
                    'name': product_obj.name,
                }
                invoice_line_list.append((0, 0, invoice_line))

            invoice_vals = {
                'partner_id': agent_id,
                'invoice_date': datetime.date.today(),
                'internal_order_bool': True,
                'move_type': 'out_invoice',  # Specify the invoice type (out_invoice for customer invoice)
                'invoice_origin': so_ids.name,
                'currency_id': so_ids.currency_id.id,
                'company_id': so_ids.company_id.id,
                'user_id': so_ids.user_id.id,
                'fiscal_position_id': so_ids.fiscal_position_id.id,
                'invoice_payment_term_id': so_ids.payment_term_id.id,
                'line_ids': invoice_line_list,
                # Add other required fields based on your needs
            }

            self.env['account.move'].create(invoice_vals)

        return True

    def add_invoice_lines(self):
        for rec in self.ret_ids:
            report = self.env['contact.report'].search([('stock_picking', '=', rec.id)])
            for reports in report:
                stock_picking = self.env['stock.picking'].search(
                    [('picking_type_code', '=', 'incoming'), ('group_id', '=', reports.stock_picking.group_id.id)])
                for res in stock_picking.move_line_ids_without_package:
                    existing_line = self.invoice_line_ids.filtered(
                        lambda line: line.product_id == res.product_id)
                    if existing_line:
                        total = res.qty_done + existing_line.quantity
                        existing_line.write({
                            'quantity': total,
                        })
                    else:
                        vals = {
                            'product_id': res.product_id.id,
                            'name': res.product_id.name,
                            'quantity': res.qty_done,
                            'price_unit': res.product_id.list_price,
                        }
                        self.write({
                            'invoice_line_ids': [(0, 0, vals)]
                        })


class AgentsPayments(models.Model):
    _description = "Agents Payments"
    _inherit = 'account.payment'

    unit_id = fields.Many2one('res.partner', domain=[('is_printing_unit', '=', True)])

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.account_payment_document_access == 'own':
            args += [('partner_id', '=', self.env.user.partner_id.id)]
        # elif self.env.user.sale_order_line_document_access == 'all':
        #     if self.env.user.has_group('base.group_erp_manager'):
        #         return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order,
        #                                                         count=count)
        #     else:
        #         user_groups = self.env.user.groups_id.ids
        #         args += ['|', ('user_id', '=', self.env.user.id), ('user_id', 'in', user_groups)]
        return super(AgentsPayments, self).search(args, offset=offset, limit=limit, order=order, count=count)


class AccountPaymentRegisterInherit(models.TransientModel):
    _description = "Agents Payments"
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        payments = self._create_payments()
        unit_payment_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        for unit in unit_payment_ids:
            for edition in unit.servie_regions:
                for district in edition.district_o2m:
                    for zones in district.zone_o2m:
                        for agents in zones.add_zones_to_line:
                            if payments.partner_id.id == agents.cc_zone.id:
                                payments.unit_id = unit.id

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action

