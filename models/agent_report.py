from odoo import api, fields, models


class ContactReport(models.Model):
    _name = "contact.report"
    _description = "contact report"
    agent = fields.Many2one('res.partner', string='Agent')
    user_id = fields.Many2one('res.users', string='User', related="agent.user_id")
    source = fields.Char('Source')
    fr_om = fields.Many2one('stock.location', 'From')
    newspaper = fields.Date(string='Newspaper Date')
    news_qty = fields.Float(string='Newspaper Quantity')
    magazine = fields.Float(string='Magzine Quantity')
    special_qty = fields.Float(string='Special Additional Quantity')
    product_name = fields.Many2one('product.template', 'Product Name')
    return_QTY = fields.Float(string='Return QTY')
    return_date = fields.Date('Return Date')
    total = fields.Float(string='Total', compute='sum_of_reports')
    credit_note = fields.Boolean('Credit Note')
    stock_picking = fields.Many2one('stock.picking', 'source')
    account_move = fields.Many2one('account.move', string='Credit Note Name')
    total_return = fields.Float(string='Returned Total Qty', compute='sum_of_reports')
    stock_picking_return = fields.Many2one('stock.picking', 'Return source')
    newspaper_return_qty = fields.Float('Returned Newspaper Qty')
    magazine_return_qty = fields.Float('Returned Magazine Qty')
    sp_return_qty = fields.Float('Returned Special Edition Qty')
    lot_id = fields.Many2one(
        'stock.lot', 'Lot Number', )
    agent_code = fields.Char('Agent Code', related='agent.agent_code')
    lot_idds = fields.Many2many('stock.lot', string='Lot Number')

    def action_account_payment(self, total, agent, ret):
        view_id = self.env.ref('account.view_move_form').id
        context = {'default_internal_order_bool': True, 'default_total': total, 'default_newsprint_agent': agent.id,
                   'default_ret_ids': ret, 'default_move_type': 'out_refund'}
        action = {
            'name': 'Credit Note',
            'view_id': view_id,
            'view_mode': 'tree',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'current',
        }
        return action

    def sum_of_reports(self):
        for rec in self:
            rec.total = rec.news_qty + rec.magazine + rec.special_qty
            rec.total_return = rec.newspaper_return_qty + rec.magazine_return_qty + rec.sp_return_qty


class DeliveryInherit(models.Model):
    _inherit = 'stock.picking'

    active = fields.Boolean('Active', default=True, tracking=True)

    # to update delivary details in agent summary
    def button_validate(self):
        p = []
        magazine = 0
        sp = 0
        for rec in self:
            # move_line_ids_without_package
            for i in rec.move_ids_without_package:
                if i.product_id.is_magazine == True:
                    magazine += i.quantity_done
                if i.product_id.is_special_edition == True:
                    sp += i.quantity_done
                if i.product_id.is_magazine != True:
                    if i.product_id.is_special_edition != True:
                        p.append(i)
        for j in p:
            for i in j:
                for res in self:
                    if res.picking_type_code == 'outgoing':
                        if res.origin.startswith('IO'):
                            self.env['contact.report'].create({
                                'agent': res.partner_id.id,
                                'news_qty': j.quantity_done,
                                'source': rec.name,
                                'magazine': magazine,
                                'special_qty': sp,
                                'stock_picking': res.id,
                                'newspaper': j.newspaper_date,
                                'lot_idds': j.lot_ids
                                # 'lot_id': i.lot_ids.id
                            })
                    elif res.picking_type_code == 'incoming':
                        agent_report = self.env['contact.report'].search(
                            [('agent', '=', res.partner_id.id), ('newspaper', '=', j.newspaper_date),
                             ('credit_note', '=', False)])
                        for agent in agent_report:
                            total_newspaper = agent.newspaper_return_qty + j.quantity_done
                            total_magazine = agent.magazine_return_qty + magazine
                            total_sp = agent.sp_return_qty + sp
                            agent.update({
                                'newspaper_return_qty': total_newspaper,
                                'magazine_return_qty': total_magazine,
                                'sp_return_qty': total_sp,
                                'stock_picking_return': res.id,
                                'return_date': fields.Datetime.now(),
                            })
        super(DeliveryInherit, self).button_validate()
