from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class RegionZone(models.Model):
    _name = 'region.zone'
    _rec_name = 'cc_zone'

    # associated_zones = fields.Char('Zone Name')
    cc_zone = fields.Many2one('res.partner', 'Agent', domain=[('is_newsprint_agent', '=', True)])
    agent_code = fields.Char('Agent Code', related='cc_zone.agent_code')
    Zone_Name = fields.Char('Zone Name')
    partner_agent = fields.Many2many('res.partner', string='Zone', readonly=True)
    Freebee_Quantity = fields.Integer(string="Free copies", compute='_conmpute_all_copies')
    newspaper_quantity = fields.Integer(string="Agent copies", compute='_conmpute_all_copies')
    Postal_copies = fields.Integer(string="Postal copies", compute='_conmpute_all_copies')
    voucher_copies = fields.Integer(string="voucher copies", compute='_conmpute_all_copies')
    promotional_copies = fields.Integer(string="promotional copies", compute='_conmpute_all_copies')
    corresspondents_copies = fields.Integer(string="corresspondent's copies", compute='_conmpute_all_copies')
    office_copies = fields.Integer(string="office copies", compute='_conmpute_all_copies')
    total_copies = fields.Integer(string="Total No of Copies", compute='_compute_total_copies')

    zones_many2one = fields.Many2one('res.partner', 'Zones')

    @api.onchange('cc_zone')
    def create_zone_name(self):
        for rec in self:
            rec.Zone_Name = rec.cc_zone.name

    # new
    @api.onchange('Freebee_Quantity', 'newspaper_quantity', 'Postal_copies', 'voucher_copies', 'promotional_copies',
                  'corresspondents_copies', 'office_copies')
    def _compute_total_copies(self):
        for rec in self:
            rec.total_copies = rec.Freebee_Quantity + rec.newspaper_quantity + rec.Postal_copies + rec.voucher_copies + rec.promotional_copies + rec.corresspondents_copies + rec.office_copies

    # compute totaling all cpoies from where the zone where and how many the zone did have value
    def _conmpute_all_copies(self):
        for z in self:
            z.newspaper_quantity = 0.0
            z.Freebee_Quantity = 0.0
            z.office_copies = 0.0
            z.voucher_copies = 0.0
            z.corresspondents_copies = 0.0
            z.promotional_copies = 0.0
            z.Postal_copies = 0.0
            for rec in self.partner_agent:
                for zone in rec.add_zones_to_line:
                    if z.cc_zone == zone.cc_zone:
                        z.newspaper_quantity += zone.newspaper_quantity_zone
                        z.Freebee_Quantity += zone.Freebee_Quantity_zone
                        z.office_copies += zone.office_copies_zone
                        z.voucher_copies += zone.voucher_copies_zone
                        z.corresspondents_copies += zone.corresspondents_copies_zone
                        z.promotional_copies += zone.promotional_copies_zone
                        z.Postal_copies += zone.Postal_copies_zone


class CirculationPartners(models.Model):
    _inherit = 'res.partner'

    active_agent = fields.Boolean('Active')
    unit_ref = fields.Char('Unit Code')
    short_code_unit = fields.Char(string='Short Code')
    unit_admin = fields.Char(string='Unit Admin Name')
    unit_admin_street = fields.Char()
    unit_admin_street2 = fields.Char()
    unit_admin_city = fields.Char()
    unit_admin_district = fields.Char()
    unit_admin_zip = fields.Char()
    cust_seq = fields.Char(string='Agent Sequence', readonly=True, copy=False, default='New')

    unit_admin_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                          domain="[('country_id', '=?', country_id)]")
    unit_admin_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    unit_location = fields.Char('Location')
    district_id = fields.Many2one('res.state.district', 'District')
    no_pages = fields.Integer('No of Pages')
    no_pages_edition = fields.Integer('No of Pages')
    no_pages_district = fields.Integer('No of Pages')
    parent_id_edition = fields.Many2one('add.new.product')
    parent_id_regions = fields.Many2one('add.new.product')
    parent_id_district = fields.Many2one('add.new.product')
    ref_district = fields.Integer('District Code')
    ref_zone = fields.Integer('Zone Code')
    ref_unit = fields.Integer('Unit Code')
    ref_edition = fields.Integer('Edition Code')
    # Agent details
    unit_code = fields.Char('Unit Code')
    agent_location = fields.Char('Location')
    agent_code = fields.Char('Agent Code')
    stop_dt = fields.Date('Stop Date')
    rt_code = fields.Integer('RT Code')
    rt_place = fields.Char('RT Place')
    std_code = fields.Integer('STD Code')
    dt_app = fields.Date('DT App')
    district_code = fields.Integer('District code')
    district_name = fields.Char('District Name')
    division_code = fields.Integer('Division code ')
    division_name = fields.Char('Division Name')
    mandal_no = fields.Integer('Mandal No')
    mandal_name = fields.Char('Mandal Name')
    constituency_code = fields.Integer('Constituency code')
    constituency_name = fields.Char('Constituency Name')
    edn_code = fields.Integer('EDN Code')
    edn_name = fields.Char('EDN Name')
    dpr_code = fields.Integer('DPR Code')
    dpr_name = fields.Char('DPR Name')
    main_code = fields.Integer('Main code')
    tsp_code = fields.Integer('TSP Code')
    dc_code = fields.Integer('DC Code')
    sub_code = fields.Integer('Sub code')
    ssb_code = fields.Integer('SSB Code')
    from_place = fields.Char('From Place')
    to_place = fields.Char('To Place')
    pm_code = fields.Integer('Pm Code')
    ee_stat = fields.Char('EE stat')
    is_additions = fields.Boolean('Is Editions', default=0)
    is_district = fields.Boolean('Is district', default=0)
    parent_id_district_o2m = fields.Many2one('res.partner')
    parent_id_zone_o2m = fields.Many2one('res.partner')
    unit_partner_id = fields.Many2one('res.partner', string="Unit Incharge")
    district_o2m = fields.One2many('res.partner', 'parent_id_district_o2m', 'District')
    zone_o2m = fields.One2many('res.partner', 'parent_id_zone_o2m', 'Associated Zone')

    region_zone_one2many = fields.One2many('region.zone', 'zones_many2one')
    is_printing_unit = fields.Boolean("Is Newprint Unit", label="Newprint Unit")
    Freebee_Quantity = fields.Integer(string="Free Copies", compute='compute_total_copies')
    newspaper_quantity = fields.Integer(string="Agent Copies", compute='compute_total_copies')
    Postal_copies = fields.Integer(string="Postal Copies", compute='compute_total_copies')
    voucher_copies = fields.Integer(string="voucher Copies", compute='compute_total_copies')
    promotional_copies = fields.Integer(string="promotional Copies", compute='compute_total_copies')
    corresspondents_copies = fields.Integer(string="corresspondent's Copies", compute='compute_total_copies')
    office_copies = fields.Integer(string="office Copies", compute='compute_total_copies')
    total_copies = fields.Integer(string="Total No of Copies", compute='_compute_total_copies')
    region_zone = fields.Many2many('region.zone', string='Agents')
    new_new = fields.Boolean(string="Manufacturin units")
    add_zones_to_line = fields.One2many('add.zones.to.line', 'res_partner')
    super_child_ids = fields.One2many('res.partner', 'parent_id', string='Contact', domain=[('active', '=', True)])
    servie_regions_line = fields.One2many('res.partner', 'parent_id')
    servie_regions = fields.Many2many(
        'res.partner',
        'res_partner_related_partner_rel',
        'partner_id',
        'related_partner_id', inverse_name="partner_id",
        string='Editions', domain=[('is_additions', '=', True)]
    )
    unit_ids = fields.Many2many(
        'res.partner',
        'res_partner_related_partner_rel',
        'partner_id',
        'related_partner_id',
        string='Editions', domain=[('is_printing_unit', '=', True)]
    )


    segment_agents = fields.Many2many(
        'res.users',
        'segment_agent_related_user_rel',
        'user_id',
        string='Segment Agents'
    )
    is_segment_incharge = fields.Boolean('Is Segment Incharge', default=0)
    is_vehicle_vendor = fields.Boolean('Is Vehicle Vendor', default=0)
    is_zone = fields.Boolean('Is Zone', default=0)
    ref = fields.Char('Reference')
    # for zones
    f_q_zone = fields.Integer(string="Free Copies")
    n_q_zone = fields.Integer(string="Agent Copies")
    p_q_zone = fields.Integer(string="Postal Copies")
    v_q_zone = fields.Integer(string="Voucher Copies")
    pr_q_zone = fields.Integer(string="Promotional Copies",
                             )
    c_c_zone = fields.Integer(string="Corresspondent's Copies",
                            )
    o_q_zone = fields.Integer(string="Office Copies")
    t_c_zone = fields.Integer(string="Total No of Copies", compute='_compute_t_co')
    meeting_count = fields.Integer("# Meetings", compute='_compute_meeting_count')
    vehicle_count = fields.Integer("Vehicles", compute='_compute_vehicle_count')
    deposit_interest = fields.Integer(string="Deposit Interest(%)", readonly=True)

    def _compute_meeting_count(self):
        for rec in self:
            if rec.is_district == True:
                rec.meeting_count = 0
            elif rec.is_zone == True:
                rec.meeting_count = 0
            elif rec.is_printing_unit == True:
                rec.meeting_count = 0
            elif rec.is_newsprint_agent == True:
                rec.meeting_count = 0
            else:
                result = rec._compute_meeting()
                rec.meeting_count = len(result.get(rec.id, []))

    def _compute_t_co(self):
        for rec in self:
            rec.t_c_zone = rec.f_q_zone + rec.n_q_zone + rec.p_q_zone + rec.v_q_zone + rec.pr_q_zone + rec.c_c_zone + rec.o_q_zone

    @api.constrains('name')
    def adding_agent_to_agents(self):
        region_zone = self.env['region.zone'].search([])
        for rec in self:
            if rec.is_newsprint_agent:
                for agent in region_zone:
                    if rec.id == agent.cc_zone.id:
                        return
                else:
                    self.env['region.zone'].create(
                        {
                            'cc_zone': rec.id
                        }
                    )

    def _get_contact_name(self, partner, name):
        return "%s" % (name)

    Associated_Units = fields.Many2many(
        'res.partner',
        'res_partner_related_partner_rel',
        'partner_id',
        'related_partner_id',
        string='Associated Units', domain=[('is_printing_unit', '=', True)], compute='compute_associated'
    )
    # , compute = 'compute_districts_parent_id'
    associated_edition = fields.Many2many(
        'res.partner',
        'res_partner_related_partner_rel',
        'partner_id',
        'related_partner_id',
        string='Associated Edition'
    )
    # , compute = 'compute_districts_parent_id'
    associated_district = fields.Many2many(
        'res.partner',
        'res_partner_related_partner_rel',
        'partner_id',
        'related_partner_id',
        string='Associated District'
    )
    unit_mains_one2many = fields.One2many('unit.mains.lines', 'res_partner_id')

    @api.onchange('Freebee_Quantity', 'newspaper_quantity', 'Postal_copies', 'voucher_copies', 'promotional_copies',
                  'corresspondents_copies', 'office_copies')
    def _compute_total_copies(self):
        for rec in self:
            rec.total_copies = rec.Freebee_Quantity + rec.newspaper_quantity + rec.Postal_copies + rec.voucher_copies + rec.promotional_copies + rec.corresspondents_copies + rec.office_copies
    def compute_associated(self):
        parents = []
        search_units = self.env['res.partner'].search([])
        for rec in self:
            for units in search_units:
                if rec in units.servie_regions:
                    parents.append(units.id)
            rec.Associated_Units = parents

    
    def compute_districts_parent_id(self):
        district_parents = []
        zone_parents = []
        search_edition = self.env['res.partner'].search([])

        for rec in self:
            for parent in search_edition:
                if rec in parent.district_o2m:
                    district_parents.append(parent.id)
                if rec in parent.zone_o2m:
                    zone_parents.append(parent.id)

            rec.associated_edition = district_parents
            rec.associated_district = zone_parents

    @api.constrains('region_zone')
    def add_region_zones(self):
        res_partner = self.env['res.partner'].search([])
        for re in res_partner:
            if re.region_zone:
                for r in re.region_zone:
                    regions = self.env['region.zone'].search([('cc_zone', '=', r.cc_zone.id)])
                    for rz in regions:
                        adds = self.env['add.zones.to.line'].create({
                            'cc_zone': rz.cc_zone.id,
                            'Freebee_Quantity_zone': rz.cc_zone.f_q_zone,
                            'newspaper_quantity_zone': rz.cc_zone.n_q_zone,
                            'Postal_copies_zone': rz.cc_zone.p_q_zone,
                            'voucher_copies_zone': rz.cc_zone.v_q_zone,
                            'promotional_copies_zone': rz.cc_zone.pr_q_zone,
                            'corresspondents_copies_zone': rz.cc_zone.c_c_zone,
                            'office_copies_zone': rz.cc_zone.o_q_zone,
                        })
                        if not re.add_zones_to_line.filtered(lambda line: line.cc_zone.id == rz.cc_zone.id):
                            re.add_zones_to_line += adds

    # to compute total number of copies
    def compute_total_copies(self):
        total_newspaper_quantity = 0
        total_Freebee_Quantity = 0
        total_Postal_copies = 0
        total_voucher_copies = 0
        total_promotional_copies = 0
        total_corresspondents_copies = 0
        total_office_copies = 0
        for total in self.add_zones_to_line:
            total_newspaper_quantity += total.newspaper_quantity_zone
            total_Freebee_Quantity += total.Freebee_Quantity_zone
            total_Postal_copies += total.Postal_copies_zone
            total_voucher_copies += total.voucher_copies_zone
            total_promotional_copies += total.promotional_copies_zone
            total_corresspondents_copies += total.corresspondents_copies_zone
            total_office_copies += total.office_copies_zone

        self.newspaper_quantity = total_newspaper_quantity
        self.Freebee_Quantity = total_Freebee_Quantity
        self.Postal_copies = total_Postal_copies
        self.promotional_copies = total_promotional_copies
        self.office_copies = total_office_copies
        self.corresspondents_copies = total_corresspondents_copies
        self.voucher_copies = total_voucher_copies

    def vehicles_count(self):
        action = self.env.ref('transport_portal.action_transport_vehicle').read()[0]
        action['domain'] = [('unit_id', '=', self.id)]
        return action

    def _compute_vehicle_count(self):
        self.vehicle_count = 0
        for vehicle in self:
            vehicle.vehicle_count = self.env['transport.vehicle'].search_count([('unit_id', '=', self.id)])


class Mains(models.Model):
    _name = 'unit.mains'
    name = fields.Char('Mains Name')
    mains_id = fields.Many2one('unit.mains')
    partner_id = fields.Many2one('res.partner', string='Customer')
    no_paper_with_ads = fields.Float('No of Pages')
    no_paper_without_ads = fields.Float('No of Pages without ads')


# model created for adding the mains in one2many in res.partner bcz prvious was creating th duplicate
# added security line security file and made changes in unit_mains_one2many fields in xml file
# maded changes in unit_mains_one2many in res.partner
class main_lines(models.Model):
    _name = 'unit.mains.lines'

    mains_id = fields.Many2one('unit.mains', string='Mains')
    no_paper_with_ads = fields.Float('No of Pages with ads', related='mains_id.no_paper_with_ads')
    no_paper_without_ads = fields.Float('No of Pages without ads', related='mains_id.no_paper_without_ads')
    res_partner_id = fields.Many2one('res.partner')


class AddZonesToLine(models.Model):
    _name = 'add.zones.to.line'

    zones_zone = fields.Many2one('region.zone', string='Regions')
    newspaper_date_zone = fields.Date('Newspaper Date')
    cc_zone = fields.Many2one('res.partner', 'Agent')

    Freebee_Quantity_zone = fields.Integer(string="Free Copies", readonly=False)
    newspaper_quantity_zone = fields.Integer(string="Agent Copies", readonly=False)
    Postal_copies_zone = fields.Integer(string="Postal Copies", readonly=False)
    voucher_copies_zone = fields.Integer(string="voucher Copies", readonly=False)
    promotional_copies_zone = fields.Integer(string="promotional Copies",
                                           readonly=False)
    corresspondents_copies_zone = fields.Integer(string="corresspondent's Copies",
                                               readonly=False)
    office_copies_zone = fields.Integer(string="office Copies", readonly=False)
    total_copies_zone = fields.Integer(string="Total No of Copies", compute='_compute_total_copies')
    res_partner = fields.Many2one('res.partner')

    @api.onchange('Freebee_Quantity_zone', 'newspaper_quantity_zone', 'Postal_copies_zone', 'voucher_copies_zone',
                  'promotional_copies_zone',
                  'corresspondents_copies_zone', 'office_copies_zone')

    def _compute_total_copies(self):
        for rec in self:
            rec.total_copies_zone = rec.Freebee_Quantity_zone + rec.newspaper_quantity_zone + rec.Postal_copies_zone + rec.voucher_copies_zone + rec.promotional_copies_zone + rec.corresspondents_copies_zone + rec.office_copies_zone



class regions_res(models.Model):
    _name = 'zone.res'

    # res_partner = fields.Many2one('res.partner','Zone Name')
    name = fields.Char('Name')
    f_q_zone = fields.Integer(string="Free Copies")
    n_q_zone = fields.Integer(string="Agent Copies")
    p_q_zone = fields.Integer(string="Postal Copies")
    v_q_zone = fields.Integer(string="voucher Copies")
    pr_q_zone = fields.Integer(string="promotional Copies",)
    c_c_zone = fields.Integer(string="corresspondent's Copies",)
    o_q_zone = fields.Integer(string="office Copies")
    t_c_zone = fields.Integer(string="Total No of Copies", compute='_compute_t_co')

    def _compute_t_co(self):
        for rec in self:
            rec.t_c_zone = rec.f_q_zone + rec.n_q_zone + rec.p_q_zone + rec.v_q_zone + rec.pr_q_zone + rec.c_c_zone + rec.o_q_zone
