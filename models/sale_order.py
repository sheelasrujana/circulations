from odoo import api, models, fields, _
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    duplicate_order_id = fields.Many2one('sale.order')
    agent_code = fields.Char('Agent Code', related='region_s.agent_code')
    agent_user_id = fields.Many2one('res.users', string="Agent User")

    category_id = fields.Many2one('product.category', string='Category')
    contact_name = fields.Many2one('res.partner', string="Regions")
    printing_unit = fields.Many2one('res.partner', string="Printing Unit")
    newspaper_date = fields.Date('Newspaper Date')  # newsly add
    magazine = fields.Integer('Magazine QTY')
    special_Edition = fields.Integer('Special Edition QTY')
    ware_locat = fields.Char('Warehouse Location')
    add_new_product_ids = fields.Many2one('add.new.product', ondelete='restrict')
    wc = fields.Many2one('mrp.workcenter', string='Manufacturing Unit')
    invisible_field = fields.Integer()
    region = fields.Char('Region')
    region_s = fields.Many2one('res.partner', 'Agents')
    location_id = fields.Many2one(
        'stock.location', 'Source Location')
    free_copies = fields.Integer(string="Free Copies")
    agent_copies = fields.Integer(string="Agent Copies")
    postal_copies = fields.Integer(string="Postal Copies")
    voucher_copies = fields.Integer(string="Voucher Copies")
    promotional_copies = fields.Integer(string="Promotional Copies")
    correspondents_copies = fields.Integer(string="Correspondent's Copies")
    office_copies = fields.Integer(string="Office Copies")
    internal_order = fields.Many2one(
        comodel_name='sale.order',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)
    demand_added = fields.Integer(string="Demand Changes")
    demand_changes = fields.Char(string="Demand Changes")
    demand_state = fields.Selection(
        selection=[
            ('increase', "Increase"),
            ('decrease', "Decrease"),
        ],
        string="Demand Status",
        readonly=True, copy=False, index=True,
        tracking=True, )
    immediately_usable_qty_today = fields.Float(string='Immediately Usable Qty Today')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.sale_order_line_document_access == 'own':
            args += [('region_s', '=', self.env.user.partner_id.id)]
        # elif self.env.user.sale_order_line_document_access == 'all':
        #     if self.env.user.has_group('base.group_erp_manager'):
        #         return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order,
        #                                                         count=count)
        #     else:
        #         user_groups = self.env.user.groups_id.ids
        #         args += ['|', ('user_id', '=', self.env.user.id), ('user_id', 'in', user_groups)]
        return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('free_copies','agent_copies','postal_copies','voucher_copies','promotional_copies', 'correspondents_copies', 'office_copies')
    def agents_copies(self):
        self.product_uom_qty = self.free_copies + self.agent_copies + self.postal_copies + self.voucher_copies + self.promotional_copies + self.correspondents_copies + self.office_copies

    @api.constrains('product_id')
    def location_ids(self):
        for rec in self:
            location = rec.product_id.bom_ids.picking_type_id.default_location_src_id.id
            rec.location_id = location

    # to change the delivary qantity of magazin
    @api.onchange('magazine')
    def add_qty_m(self):
        for add in self:
            add.product_uom_qty = add.magazine

    # to change the delivary qantity of the special edition quantity
    @api.onchange('special_Edition')
    def add_qty_s(self):
        for add in self:
            add.product_uom_qty = add.special_Edition

    # depends on warehouse adding product
    @api.onchange('wc')
    def product_wc(self):
        wc = self.env['mrp.workcenter'].search([('name', '=', self.wc.name)])
        for i in wc:
            for j in i.capacity_ids:
                self.product_id = j.product_id

        if not self.contact_name:
            self.contact_name = self.order_id.partner_shipping_id

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.region_s:
            res.update({'partner_id': self.region_s.id or self.order_id.partner_shipping_id.id or False,
                        'newspaper_date': self.newspaper_date, 'res_unit': self.printing_unit.id, 'regions': self.region, 'internal_order_delivary': True})
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    res_unit = fields.Many2one('res.partner', string='Printing Unit')

    def _key_assign_picking(self):
        keys = super(StockMove, self)._key_assign_picking()
        return keys + (self.partner_id,)

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = super(StockMove, self)._search_picking_for_assignation()
        if self.sale_line_id and self.partner_id:
            picking = picking.filtered(lambda l: l.partner_id.id == self.partner_id.id)
            if picking:
                picking = picking[0]
        return picking


class ProductTemplate(models.Model):
    _inherit = "product.template"

    variant_bom_ids = fields.One2many('mrp.bom', 'product_id', 'BOM Product Variants')
    scrap_location = fields.Many2one('stock.location', 'Scrap Location')
    is_newspaper = fields.Boolean('Is Newspaper?')


class ProductProductNew(models.Model):
    _inherit = "product.product"

    is_magazine = fields.Boolean('Is Magazine?')
    is_special_edition = fields.Boolean('Is Special Edition?')
    is_return = fields.Boolean('Is Return?')
    is_newspaper = fields.Boolean('Is Newspaper?')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_duplicating = fields.Boolean('sale order duplicating', default=False)
    order_line_duplicate = fields.One2many('sale.order.line', 'order_id')
    new_seq = fields.Char(string='Internal Order Number', readonly=True, required=True, default='NEW')
    add_new_product = fields.One2many('add.new.product', 'order_id')
    internal_order = fields.Boolean('boolen internal', default=False)
    timedelta_prev_day = fields.Float(compute='_compute_timedelta_prev_day')
    prev_day_date = fields.Date(compute='_compute_prev_day_date')
    free_copies = fields.Integer(string="Free Copies", compute="_compute_indent_copies")
    agent_copies = fields.Integer(string="Agent Copies", compute="_compute_indent_copies")
    postal_copies = fields.Integer(string="Postal Copies", compute="_compute_indent_copies")
    voucher_copies = fields.Integer(string="Voucher Copies", compute="_compute_indent_copies")
    promotional_copies = fields.Integer(string="Promotional Copies", compute="_compute_indent_copies")
    correspondents_copies = fields.Integer(string="Correspondent's Copies", compute="_compute_indent_copies")
    office_copies = fields.Integer(string="Office Copies", compute="_compute_indent_copies")
    demand_changes = fields.Integer(string="Demand Changes", compute="_compute_indent_copies")
    total_copies = fields.Integer(string="Total Copies", compute="_compute_indent_copies")
    classified_bool_field = fields.Boolean(default=False)
    unit_name = fields.Many2one('res.partner', string='Unit', related='add_new_product.partner_id')

    def _compute_prev_day_date(self):
        for order in self:
            order.prev_day_date = fields.Date.to_string(
                fields.Date.from_string(fields.Date.today()) - timedelta(days=1))

    def _compute_indent_copies(self):
        self.office_copies = 0
        self.correspondents_copies = 0
        self.promotional_copies = 0
        self.voucher_copies = 0
        self.free_copies = 0
        self.agent_copies = 0
        self.postal_copies = 0
        self.total_copies = 0
        self.demand_changes = 0
        for order in self:
            for order_line in order.order_line:
                if order_line.product_id.is_newspaper == True:
                    order.free_copies += order_line.free_copies
                    order.agent_copies += order_line.agent_copies
                    order.postal_copies += order_line.postal_copies
                    order.voucher_copies += order_line.voucher_copies
                    order.promotional_copies += order_line.promotional_copies
                    order.correspondents_copies += order_line.correspondents_copies
                    order.office_copies += order_line.office_copies
                    order.demand_changes += int(order_line.demand_changes)
                    order.total_copies += order_line.product_uom_qty

    def action_yesterday_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Yesterday Orders',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': "[('create_date', '>=', (datetime.datetime.combine(context_today(), datetime.time(0, 0, 0)) - timedelta(days=1)).date()), ('create_date', '<=', (datetime.datetime.combine(context_today(), datetime.time(23, 59, 59)) - timedelta(days=1)).date()))]",
        }

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        today_records = self._context.get('search_default_today_records', False)
        if today_records:
            args.append(('create_date', '>=',
                         fields.Datetime.to_string(fields.Datetime.now().replace(hour=0, minute=0, second=0))))
            args.append(('create_date', '<=',
                         fields.Datetime.to_string(fields.Datetime.now().replace(hour=23, minute=59, second=59))))
        return super(SaleOrder, self).search(args, offset, limit, order, count)

    @api.model
    def create(self, vals_list):
        if vals_list.get('internal_order') == True:
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'internal.order') or _("New")
            vals_list['new_seq'] = vals_list['name']

        return super(SaleOrder, self).create(vals_list)

    mrp_order_count = fields.Integer(
        compute='_compute_mrp_order_count',
        string='MRP Order Count',
        readonly=True
    )

    def view_mrp_orders(self):
        for res in self.env.user.partner_id.segment_agents.ids:
            rem = self.env['res.users'].browse(res)
            for user in  self.env.user.partner_id.segment_agents.partner_id.segment_agents.ids:
                r = self.env['res.users'].browse(user)
                for user_id in self.env.user.partner_id.segment_agents.partner_id.segment_agents.partner_id.segment_agents.ids:
                    m = self.env['res.users'].browse(user_id)
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('origin', '=', self.name)]
        return action

    @api.depends('name')
    def _compute_mrp_order_count(self):
        self.mrp_order_count = 0
        for order in self:
            order.mrp_order_count = self.env['mrp.production'].search_count([
                ('origin', '=', order.name)
            ])

    state_duplicate = fields.Selection(
        selection=[
            ('draft', "Demand"),
            ('sent', "Demand Sent"),
            ('sale', "Confirmed"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    @api.constrains('state')
    def states_change(self):
        if self.state == 'draft':
            self.state_duplicate = 'draft'
        elif self.state == 'sent':
            self.state_duplicate = 'sent'
        elif self.state == 'sale':
            self.state_duplicate = 'sale'
        elif self.state == 'done':
            self.state_duplicate = 'done'
        elif self.state == 'cancel':
            self.state_duplicate = 'cancel'

    def additional_copies(self):
        for lines in self.order_line:
            if lines.demand_state not in ['increase', 'decrease']:
                demand_request = self.env['demand.request'].search(
                    [('Agent_id', '=', lines.region_s.id), ('specific_date', '=', lines.newspaper_date)])
                total_demand_changes = 0
                for demand in demand_request:
                    if demand and demand.state == 'approved':
                        if demand.no_of_additional_copies:
                            total = lines.product_uom_qty + demand.no_of_additional_copies
                            total_demand_changes += demand.no_of_additional_copies
                            lines.update({
                                'product_uom_qty': total,
                                'demand_added': total_demand_changes,
                                'demand_state': 'increase',
                                'magazine': total,
                            })
                        elif demand.decrease_additional_copies:
                            total = lines.product_uom_qty - demand.decrease_additional_copies
                            total_demand_changes += demand.decrease_additional_copies
                            lines.update({
                                'product_uom_qty': total,
                                'demand_added': total_demand_changes,
                                'demand_state': 'decrease',
                                'magazine': total,
                            })

    @api.constrains('add_new_product')
    def lines_added(self):
        # By this method values are passing from add_new_product to sale.order.line based and child_ids
        line_ids = []
        for lines in self.add_new_product:
            if lines.check_box == False:
                line_ids.append(lines)
                lines.check_box = True
        for partner in line_ids:
            # partner gives records of add_new_product
            for regions in partner.regions_contact:
                for agent in regions.region_zone:
                    for zones in regions.add_zones_to_line:
                        if agent.cc_zone.name == zones.cc_zone.name:
                            if agent.cc_zone.active_agent == True:
                                if partner.product_id.is_magazine == True:

                                    self.env['sale.order.line'].create({
                                        'printing_unit': partner.partner_id.id,
                                        # 'region': regions.Zone_Name,
                                        'region_s': agent.cc_zone.id,
                                        'product_id': partner.product_id.id,
                                        'agent_user_id': zones.cc_zone.user_id.id,
                                        # passing values from total no copies to product_qty
                                        'free_copies': zones.Freebee_Quantity_zone,
                                        'agent_copies': zones.newspaper_quantity_zone,
                                        'postal_copies': zones.Postal_copies_zone,
                                        'voucher_copies': zones.voucher_copies_zone,
                                        'promotional_copies': zones.promotional_copies_zone,
                                        'correspondents_copies': zones.corresspondents_copies_zone,
                                        'office_copies': zones.office_copies_zone,
                                        'product_uom_qty': zones.total_copies_zone,
                                        'magazine': zones.total_copies_zone,
                                        'contact_name': regions.id,
                                        # 'contact_name_Duplicate': child.name,
                                        'order_id': self.id,
                                        'add_new_product_ids': partner.id,
                                        'newspaper_date': partner.newspaper_date,  # new 28 apr
                                        # based on this the product_uom_qty field getting hide
                                        'invisible_field': 1,
                                    })
                                elif partner.product_id.is_special_edition == True:
                                    self.env['sale.order.line'].create({
                                        'printing_unit': partner.partner_id.id,
                                        # 'region': regions.Zone_Name,
                                        'region_s': agent.cc_zone.id,
                                        'product_id': partner.product_id.id,
                                        'agent_user_id': zones.cc_zone.user_id.id,
                                        # passing values from total no copies to product_qty
                                        'free_copies': zones.Freebee_Quantity_zone,
                                        'agent_copies': zones.newspaper_quantity_zone,
                                        'postal_copies': zones.Postal_copies_zone,
                                        'voucher_copies': zones.voucher_copies_zone,
                                        'promotional_copies': zones.promotional_copies_zone,
                                        'correspondents_copies': zones.corresspondents_copies_zone,
                                        'office_copies': zones.office_copies_zone,
                                        'product_uom_qty': zones.total_copies_zone,
                                        'special_Edition': zones.total_copies_zone,
                                        'contact_name': regions.id,
                                        # 'contact_name_Duplicate': child.name,
                                        'order_id': self.id,
                                        'add_new_product_ids': partner.id,
                                        'newspaper_date': partner.newspaper_date,  # new 28 apr
                                        # based on this the product_uom_qty field getting hide
                                        'invisible_field': 1,
                                    })
                                else:
                                    self.env['sale.order.line'].create({
                                        'printing_unit': partner.partner_id.id,
                                        # 'region': regions.Zone_Name,
                                        'region_s': agent.cc_zone.id,
                                        'product_id': partner.product_id.id,
                                        'agent_user_id': zones.cc_zone.user_id.id,
                                        # passing values from total no copies to product_qty
                                        'free_copies': zones.Freebee_Quantity_zone,
                                        'agent_copies': zones.newspaper_quantity_zone,
                                        'postal_copies': zones.Postal_copies_zone,
                                        'voucher_copies': zones.voucher_copies_zone,
                                        'promotional_copies': zones.promotional_copies_zone,
                                        'correspondents_copies': zones.corresspondents_copies_zone,
                                        'office_copies': zones.office_copies_zone,
                                        'product_uom_qty': zones.total_copies_zone,
                                        'contact_name': regions.id,
                                        # 'contact_name_Duplicate': child.name,
                                        'order_id': self.id,
                                        'add_new_product_ids': partner.id,
                                        'newspaper_date': partner.newspaper_date,
                                    })
        self.additional_copies()

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

    def redirect_to_sale_order(self):
        # Retrieve the date parameter from the context (you can pass it from the action)
        date_str = self._context.get('date')
        user = self.env.uid
        # Parse the date string into a date object
        date = fields.Date.from_string(date_str)
        today = fields.Date.today()
        user_id = self.env['res.users'].browse(user)
        current_day = datetime.today().strftime('%Y-%m-%d')
        # Find the sale order record based on the given date
        sale_order = self.search([('internal_order', '=', True), ('create_date', '>=', current_day + ' 00:00:00'),
            ('create_date', '<', current_day + ' 23:59:59')])
        domain = [('id', '=', sale_order.id)]
        return {
                'name': _('Ship On-Board Details'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': domain,
                'views_id': False,
                'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],

        }


class AddNewProduct(models.Model):
    _name = 'add.new.product'

    partner_id = fields.Many2one('res.partner', string="Printing Units", domain=[('is_printing_unit', '=', True)])
    newspaper_date = fields.Date('Newspaper Date')  # newsly add
    product_id = fields.Many2one('product.product', string="Products")
    qty = fields.Integer('Number of Copies', compute='total_qty')
    with_ads = fields.Integer('With Ads', compute='_compute_ads', readonly=False, store=True)
    without_ads = fields.Integer('Without Ads', compute='_compute_ads', readonly=False, store=True)
    check_box = fields.Boolean('State')
    check_box2 = fields.Boolean('State')
    order_id = fields.Many2one('sale.order')
    order_line = fields.Many2one('sale.order.line')
    regions_contact = fields.Many2many('res.partner', 'parent_id_regions',
                                       string='Regions')
    edition_contacts = fields.Many2many('res.partner', 'parent_id_edition', string='Editions')
    district_contacts = fields.Many2many('res.partner', 'parent_id_district', string='Districts')
    mains_contact = fields.Many2many('unit.mains', string='Mains')
    hide_add_m = fields.Boolean(default=False)
    hide_add_s = fields.Boolean(default=False)

    @api.onchange('partner_id')
    def adding_zone_from_addition(self):
        for rec in self:
            zone = []
            edition = []
            district = []
            for additions in rec.partner_id.servie_regions:
                edition.append(additions.id)
                for districts in additions.district_o2m:
                    district.append(districts.id)
                    for zones in districts.zone_o2m:
                        zone.append(zones.id)
            else:
                rec.regions_contact = None
                rec.edition_contacts = None
                rec.district_contacts = None
            rec.regions_contact = zone
            rec.edition_contacts = edition
            rec.district_contacts = district

    @api.constrains('product_id', 'mains_contact')
    @api.onchange('mains_contact')
    def main_no_pages(self):
        total = 0
        for rec in self:
            for no in rec.mains_contact:
                total += no.no_paper_with_ads
            for region_no in rec.regions_contact:
                region_no.no_pages = total

    @api.onchange('partner_id')
    def partner_mains(self):
        partner_id_regions = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        mains = []
        for regions in partner_id_regions.unit_mains_one2many:
            mains.append(regions.mains_id.id)
        else:
            self.mains_contact = None
        self.mains_contact = mains

    def magazine(self):
        # newone unit_id
        product_id = self.env['product.product'].search(
            [('is_magazine', '=', True), ('unit_id', '=', self.partner_id.id)])
        # newone
        if product_id:
            self.create({
                'partner_id': self.partner_id.id,
                'product_id': product_id.id,
                'qty': self.qty,
                'regions_contact': self.regions_contact,
                'newspaper_date': self.newspaper_date,
                'order_id': self.order_id.id,
                'edition_contacts': self.edition_contacts,
                'district_contacts': self.district_contacts,
                'hide_add_m': True
            })
            self.order_id.lines_added()

    def special_edition(self):
        product_id = self.env['product.product'].search([('is_special_edition', '=', True)])

        self.create({
            'partner_id': self.partner_id.id,
            'product_id': product_id.id,
            'qty': self.qty,
            'regions_contact': self.regions_contact,
            'newspaper_date': self.newspaper_date,
            'order_id': self.order_id.id,
            'edition_contacts': self.edition_contacts,
            'district_contacts': self.district_contacts,
            'hide_add_s': True,

        })
        self.order_id.lines_added()

    def free_bee(self):
        self.create({
            'partner_id': self.partner_id.id,
            'product_id': 3,
            'qty': 1.0,
            'order_id': self.order_id.id
        })
        for j in self.partner_id.child_ids:
            parent_partner = self.env['sale.order.line'].search([('contact_name', '=', j.id)])
            for qty in parent_partner:
                qty.free_bee_checkbox = True

    # deleting values from add.new.product to sale.order.line
    @api.model
    def unlink(self):
        for unlinking in self:
            self.env['sale.order.line'].search([('add_new_product_ids', '=', unlinking.id)]).unlink()
        super(AddNewProduct, self).unlink()

    # with_ads and without_ads values update
    @api.onchange('partner_id', 'mains_contact')
    def _compute_ads(self):
        for line in self:
            if len(line.mains_contact) > 1:
                line.with_ads = 0.00
                line.without_ads = 0.00
            else:
                set_qty = self.env['unit.mains'].search([('name', '=', line.mains_contact.name)])
                for ads in set_qty:
                    line.with_ads = ads.no_paper_with_ads
                    line.without_ads = ads.no_paper_without_ads


    # updating the qty based total number qty in sale order line for particular agent added to add.new.product .qty field
    def total_qty(self):
        for i in self:
            sum = 0
            for lines in self.order_id.order_line:
                if i.id == lines.add_new_product_ids.id:
                    sum += lines.product_uom_qty
            i.qty = sum


class StockRuleInherit(models.Model):
    _inherit = 'stock.lot'

    newspaper_date = fields.Date('NewsPaper Date')
    return_date = fields.Integer('Return Quantity')
    order_qty = fields.Integer(string='Order Quantity', readonly=True)
    active = fields.Boolean('Active', default=True, tracking=True)


class DeliveryInheritence(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
                               values):
        res = super(DeliveryInheritence, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id,
                                                                      name, origin, company_id, values)
        res['newspaper_date'] = values.get('newspaper_date', False)
        res['res_unit'] = values.get('res_unit', False)
        return res


class QuotationInherit(models.Model):
    _inherit = 'stock.move'

    newspaper_date = fields.Date(string='Date')
    region = fields.Char('Region')
    res_unit = fields.Many2one('res.partner', string='Printing Unit')


class StockRegion(models.Model):
    _inherit = 'stock.picking'
    _order = 'id desc'

    regions = fields.Char('Regions')
    sale_bool = fields.Boolean('sale bool')

    def action_assign(self):
        for res in self:
            if res.origin:
                if res.origin.startswith('IO'):
                    for rec in self:
                        for line in rec.move_line_ids_without_package:
                            if line.product_id.bom_ids.picking_type_id:
                                location = line.product_id.bom_ids.picking_type_id.default_location_dest_id.id
                                line.location_id = location
                        for moves in rec.move_ids_without_package:
                            if moves.product_id.bom_ids.picking_type_id:
                                location = moves.product_id.bom_ids.picking_type_id.default_location_dest_id.id
                                moves.location_id = location
            # if res.picking_type_code == 'incoming':
            #     if res.group_id.name.startswith('IO'):
            #         for rec in res.move_ids_without_package:
            #             if rec.product_id.scrap_location:
            #                 rec.location_dest_id = rec.product_id.scrap_location.id
        return super(StockRegion, self).action_assign()

    def button_validate(self):
        for res in self:
            if res.picking_type_code == 'incoming':
                for rec in res.move_line_ids_without_package:
                    lot_number = self.env['stock.lot'].search([('name', '=', rec.lot_id.name)])
                    for qty in lot_number:
                        total = qty.return_date + rec.qty_done
                        lot_number.update({
                            'return_date': total
                        })
        super(StockRegion, self).button_validate()

    # This function for bulk check_availability in Delivery
    def check_availability(self):
        for check in self:
            check.action_assign()

    # This function for bulk set_quantities in Delivery
    def action_set_quantities_to_reservation_new(self):
        for check in self:
            check.action_set_quantities_to_reservation()

    @api.model
    def create(self, vals_list):
        picking_type = self.env['stock.picking.type'].browse(vals_list.get('picking_type_id'))
        if vals_list.get('origin'):
            if vals_list.get('origin').startswith('IO'):
                if picking_type.name == 'Delivery Orders':
                    res_partner = self.env['res.partner'].browse(vals_list['partner_id'])
                    vals_list['name'] = str(res_partner.agent_code) + self.env['ir.sequence'].next_by_code(
                        'delivery.order') or _("New")
        if picking_type.name == 'Returns':
            # origin = vals_list['origin']
            # stock_picking = origin.split('Return of ')[1]
            # stock_id = self.env['stock.picking'].search([('name', '=', stock_picking)])
            # if stock_id.origin.startswith('IO'):
            res_partner = self.env['res.partner'].browse(vals_list['partner_id'])
            vals_list['name'] = str(res_partner.agent_code) + self.env['ir.sequence'].next_by_code(
                'ret.order') or _("New")
        return super(StockRegion, self).create(vals_list)





