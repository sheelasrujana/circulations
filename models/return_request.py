from odoo import api, fields, models
from datetime import datetime, timedelta
import datetime


class ReturnRequest(models.Model):
    _name = 'return.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'agent_id'
    _order = 'id desc'

    from_date = fields.Date(string="Form Date", trcking=True)
    to_date = fields.Date(string="To Date", trcking=True)
    agent_id = fields.Many2one('res.partner', 'Agent', domain=[('is_newsprint_agent', '=', True)])
    state = fields.Selection(
        selection=[
            ('new', "New"),
            ('waiting', "Waiting for approval"),
            ('approved', "Approved"),
            ('news_paper_received', "New Paper Received"),
            ('credit_note_done', "Credit Note Done"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True, store=True)
    return_request_line = fields.One2many('return.request.line', 'return_id')
    product_news_paper_id = fields.Many2one('product.product', string="Daily News Paper")
    product__magazine_id = fields.Many2one('product.product', string="Magazine")
    select_list = fields.Boolean(string="Select List")
    credit_note_count = fields.Integer(
        compute='_compute_credit_note_count',
        string='Credit Note Count',
        readonly=True
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.return_request_document_access == 'own':
            args += [('agent_id', '=', self.env.user.partner_id.id)]
        # elif self.env.user.sale_order_line_document_access == 'all':
        #     if self.env.user.has_group('base.group_erp_manager'):
        #         return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order,
        #                                                         count=count)
        #     else:
        #         user_groups = self.env.user.groups_id.ids
        #         args += ['|', ('user_id', '=', self.env.user.id), ('user_id', 'in', user_groups)]
        return super(ReturnRequest, self).search(args, offset=offset, limit=limit, order=order, count=count)

    def view_credit_note(self):
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        action['domain'] = [('return_id', '=', self.id)]
        return action

    def _compute_credit_note_count(self):
        self.credit_note_count = 0
        for return_id in self:
            return_id.credit_note_count = self.env['account.move'].search_count([
                ('return_id', '=', return_id.id)
            ])

    def send_return_request_mail(self):
        template = self.env.ref('sales_circulation.return_request_email_template')
        for rec in self:
            template.send_mail(rec.id)
            rec.state = 'waiting'

    @api.onchange('select_list')
    def onchange_select_list(self):
        if self.select_list:
            for line in self.return_request_line:
                line.select = True
        else:
            for line in self.return_request_line:
                line.select = False

    def credit_note(self):
        return_request_line = self.env['return.request.line'].search([('return_id', '=', self.id)])
        product_list = []
        if return_request_line:
            for return_line in return_request_line:
                product_type = self.env['product.product'].search(
                    [('is_return', '=', True), ('return_type', '=', return_line.return_type)], limit=1)
                for product in product_type:
                    if product.id not in product_list:
                        product_list.append(product.id)
        invoice_line_list = []
        return_list = []
        for product in product_list:
            product_obj = self.env['product.product'].browse(product)
            for return_line in product_obj:
                return_request_line = self.env['return.request.line'].search([('return_type', '=', return_line.return_type)])
                total_copies = 0
                for total_weight in return_request_line:
                    total_copies += total_weight.weight
                invoice_line = {
                    'product_id': product_obj.id,
                    'quantity': total_copies,
                    'price_unit': product_obj.lst_price,
                    'product_uom_id': product_obj.uom_id.id,
                    'name': product_obj.name,
                }
                invoice_line_list.append((0, 0, invoice_line))
        user = self.env.uid
        # Parse the date string into a date object
        user_id = self.env['res.users'].browse(user)
        invoice_vals = {
            'partner_id': self.agent_id.id,
            'invoice_date': datetime.date.today(),
            'internal_order_bool': True,
            'return_request_bool': True,
            'move_type': 'out_refund',  # Specify the invoice type (out_invoice for customer invoice)
            'return_id': self.id,
            'user_id': user_id.id,
            'line_ids': invoice_line_list,
            # Add other required fields based on your needs
        }

        self.env['account.move'].create(invoice_vals)

        return True

    def return_request_schedule(self):
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1, day=1) - timedelta(days=1))
        agents_ids = self.env['res.partner'].search([('is_newsprint_agent', '=', True), ('active_agent', '=', True)])
        for agent in agents_ids:
            vals = {
                'agent_id': agent.id,
                'from_date': first_day_of_month,
                'to_date': last_day_of_month,
                'state': 'new',
                # Add other field values as needed
            }
            self.env['return.request'].create(vals)
        return True


class ReturnRequestLines(models.Model):
    _name = 'return.request.line'

    date = fields.Date(string="Date")
    no_of_copies = fields.Integer(string="No Of Copies")
    is_credit_done = fields.Boolean(string="Is Credit Done?", readonly=True)
    return_id = fields.Many2one('return.request')
    product_id = fields.Many2one('product.product', string="Product")
    return_true = fields.Boolean()
    product_type = fields.Selection(
        selection=[
            ('newspaper', "NewsPaper"),
            ('magazine', "Magazine"),
        ],
        string="Product Type", )
    return_type = fields.Selection(
        selection=[
            ('full_paper', "Full Paper"),
            ('master_head', "Master Head"),
        ],
        string="Return Type", )
    weight = fields.Float(string="Weight")
    state = fields.Selection(
        selection=[
            ('new', "New"),
            ('waiting', "Waiting for approval"),
            ('approved', "Approved"),
            ('news_paper_received', "New Paper Received"),
            ('credit_note_done', "Credit Note Done"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='new')
    select = fields.Boolean()
    select_list = fields.Boolean()

    def send_return_request_mail(self):
        template = self.env.ref('sales_circulation.return_request_email_template')
        for rec in self:
            template.send_mail(rec.id)
            rec.state = 'waiting'

    def approve_return_request(self):
        # Extend the Return Request model to add a method for creating the stock picking return order
        # -> unit_name is used for search unit using agent name
        unit_name = self.env['res.partner'].search([('unit_ref', '=', self.return_id.agent_id.unit_code)], limit=1)
        # -> destination_location Is used for to get the scrap location
        destination_location = self.env['stock.location'].search([('scrap_location', '=', True), ('unit_id', '=', unit_name.id)], limit=1)
        # -> source_location is used for to get the source location of product
        source_location = self.env['stock.location'].search([('is_partner_location', '=', True)], limit=1)
        # -> stock_picking_type for to create the return receipt
        stock_picking_type = self.env['stock.picking.type'].search([('is_return_picking_type', '=', True)], limit=1)
        # -> creating the return picking
        return_picking = self.env['stock.picking'].create({
            'picking_type_id': stock_picking_type.id,
            'return_line': self.id,
            # Adjust this to the ID of your return picking type
            'partner_id': self.return_id.agent_id.id,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id,
        })
       # You may need to adjust the move creation based on your specific requirements
        product_type = self.env['product.product'].search([('is_return', '=', True), ('return_type', '=', self.return_type)], limit=1)
        # -> adding the move to crated stock picking
        move_vals = {
            'name': self.return_type,
            'product_id': product_type.id,
            'product_uom_qty': self.weight,
            'quantity_done': self.weight,
            'newspaper_date': self.date,
            'product_uom': product_type.uom_id.id,
            'picking_id': return_picking.id,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id,
        }
        self.env['stock.move'].create(move_vals)

        # Confirm the return picking
        return_picking.action_confirm()

        # Assign the picking to the available stock move
        return_picking.action_assign()
        self.state = 'approved'

        return return_picking

    def write(self, values):
        result = super(ReturnRequestLines, self).write(values)
        # Get the unique set of states from all sale order lines
        line_states = self.mapped('state')
        # If all sale order lines have the same state, update the main sale order's state
        if len(line_states) == 1:
            new_state = line_states[0]
            self.return_id.write({'state': new_state})
        return result


class ProductProductReturn(models.Model):
    _inherit = "product.product"

    is_return = fields.Boolean('Is Return?')
    return_type = fields.Selection(
        selection=[
            ('full_paper', "Full Paper"),
            ('master_head', "Master Head"),
        ],
        string="Return Type",)
    unit_id = fields.Many2one('res.partner',string="Unit Name", domain=[('is_printing_unit', '=', True)])


class StockLocationReturn(models.Model):
    _inherit = "stock.location"

    unit_id = fields.Many2one('res.partner',string="Unit Name", domain=[('is_printing_unit', '=', True)])
    is_partner_location = fields.Boolean('Is Partner Location?')


class StockPickingTypeReturn(models.Model):
    _inherit = "stock.picking.type"

    is_return_picking_type = fields.Boolean('Is Return Picking?')


class StockPickingReturn(models.Model):
    _inherit = "stock.picking"

    return_line = fields.Many2one('return.request.line', string="Return Line Id")

    def button_validate(self):
        # -> This is for searching the return request line,after validating the return the return request record changes in to news paper received
        return_request_line = self.env['return.request.line'].search([('id', '=', self.return_line.id)])
        return_request_line.state = 'news_paper_received'
        return super(StockPickingReturn, self).button_validate()


class ProductTemplateReturn(models.Model):
    _inherit = "product.template"

    is_return = fields.Boolean('Is Return?')
    is_transportation = fields.Boolean('Is Transportation?')
    return_type = fields.Selection(
        selection=[
            ('full_paper', "Full Paper"),
            ('master_head', "Master Head"),
        ],
        string="Return Type",)
    unit_id = fields.Many2one('res.partner',string="Unit Name", domain=[('is_printing_unit', '=', True)])







