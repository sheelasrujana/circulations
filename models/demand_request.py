from odoo import api, fields, models, _
from datetime import time, timedelta, datetime
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


class DemandRequest(models.Model):
    _name = 'demand.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'Agent_id'
    _order = 'id desc'

    Agent_id = fields.Many2one('res.partner', 'Agent', domain=[('is_newsprint_agent', '=', True)],
                               default=lambda self: self.env.user.partner_id.id, tracking=True)
    Agent_copies = fields.Integer('Agent Current Copies')
    permanent_date = fields.Date('Permanent Date', tracking=True)
    specific_date = fields.Date('Specific Date', tracking=True, default=datetime.today()+timedelta(1))
    specific_time = fields.Float('Specific Time', tracking=True)
    selection_additional_type = fields.Selection(
        selection=[
            ('increase_additional', "Increase of Additional Copies"),
            ('decrease_additional', "Decrease of Additional Copies"),
        ], string='Update Demand', tracking=True)
    no_of_additional_copies = fields.Integer('Increase of Additional Copies', tracking=True)
    decrease_additional_copies = fields.Integer('Decrease of Additional Copies', tracking=True)
    selection_update_agent_copies = fields.Selection(
        selection=[
            ('increase', "Increase Copies"),
            ('decrease', "Decrease Copies"),
        ], string='Demand Update Type', tracking=True)
    update_agent_copies = fields.Integer('Increase Agent Copies', tracking=True)
    decrease_agent_copies = fields.Integer('Decrease Agent Copies', tracking=True)
    demand_changes = fields.Integer('Demand Changes', tracking=True, compute="compute_demand_changes")
    selection_field = fields.Selection(
        selection=[
            ('permanent', "Permanent"),
            ('specific_date', "Specific date"),
        ], string='Demand Type', tracking=True)
    state = fields.Selection(
        selection=[
            ('new', "New"),
            ('waiting', "Waiting for approval"),
            ('approved', "Approved"),
            ('rejected', "Rejected"),

        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='new')
    demand_state = fields.Selection(
        selection=[
            ('increase', "Increase"),
            ('decrease', "Decrease"),
        ],
        string="Demand Status",
        readonly=True, copy=False, index=True,
        tracking=True,)
    total_copies = fields.Integer(string='Total Copies', tracking=True)
    free_copies = fields.Integer(string="Free copies", tracking=True)
    postal_copies = fields.Integer(string="Postal copies", tracking=True)
    voucher_copies = fields.Integer(string="Voucher copies", tracking=True)
    promotional_copies = fields.Integer(string="Promotional copies", tracking=True)
    correspondents_copies = fields.Integer(string="Correspondent's copies", tracking=True)
    office_copies = fields.Integer(string="Office copies", tracking=True)
    reject_reason = fields.Text(string="Reject Reason", tracking=True)
    unit_id = fields.Many2one('res.partner', string="Associated Unit")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.demand_request_document_access == 'own':
            args += [('Agent_id', '=', self.env.user.partner_id.id)]
        # elif self.env.user.sale_order_line_document_access == 'all':
        #     if self.env.user.has_group('base.group_erp_manager'):
        #         return super(SaleOrderLine, self).search(args, offset=offset, limit=limit, order=order,
        #                                                         count=count)
        #     else:
        #         user_groups = self.env.user.groups_id.ids
        #         args += ['|', ('user_id', '=', self.env.user.id), ('user_id', 'in', user_groups)]
        return super(DemandRequest, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('update_agent_copies', 'decrease_agent_copies', 'Agent_copies')
    def _onchange_total_copies_permanent(self):
        "This is for calculating the total copies for permanent"
        for record in self:
            if record.selection_update_agent_copies == 'increase':
                record.total_copies = record.Agent_copies + record.update_agent_copies
            elif record.selection_update_agent_copies == 'decrease':
                record.total_copies = record.Agent_copies - record.decrease_agent_copies
            else:
                record.total_copies = record.Agent_copies

    @api.onchange('no_of_additional_copies', 'decrease_additional_copies', 'Agent_copies')
    def _onchange_total_copies_specific_date(self):
        "This is for calculating the total copies for specific date"
        for record in self:
            if record.selection_additional_type == 'increase_additional':
                record.total_copies = record.Agent_copies + record.no_of_additional_copies
            elif record.selection_additional_type == 'decrease_additional':
                record.total_copies = record.Agent_copies - record.decrease_additional_copies
            else:
                record.total_copies = record.Agent_copies

    @api.onchange('Agent_id')
    def agent_copies(self):
        for rec in self:
            rec.Agent_copies = rec.Agent_id.n_q_zone
            rec.free_copies = rec.Agent_id.f_q_zone
            rec.postal_copies = rec.Agent_id.p_q_zone
            rec.voucher_copies = rec.Agent_id.v_q_zone
            rec.promotional_copies = rec.Agent_id.pr_q_zone
            rec.correspondents_copies = rec.Agent_id.c_c_zone
            rec.office_copies = rec.Agent_id.o_q_zone
            if rec.Agent_id.unit_code:
                unit_id = self.env['res.partner'].search([('unit_ref', '=', rec.Agent_id.unit_code)], limit=1)
                rec.unit_id = unit_id.id

    @api.onchange('specific_date')
    def _onchange_specific_date(self):
        for rec in self:
            if datetime.today().date() == rec.specific_date or datetime.today().date()-timedelta(1) == rec.specific_date:
                raise UserError(_("Select the tomorrow's date or future date only"))

    def compute_demand_changes(self):
        for rec in self:
            rec.demand_changes = 0
            if rec.no_of_additional_copies:
                rec.demand_changes = rec.no_of_additional_copies
                rec.demand_state = 'increase'
            elif rec.decrease_additional_copies:
                rec.demand_changes = rec.decrease_additional_copies
                rec.demand_state = 'decrease'
            elif rec.update_agent_copies:
                rec.demand_changes = rec.update_agent_copies
                rec.demand_state = 'increase'
            elif rec.decrease_agent_copies:
                rec.demand_changes = rec.decrease_agent_copies
                rec.demand_state = 'decrease'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        template = self.env.ref('sales_circulation.demand_reject_email_template')
        for rec in self:
            if rec.reject_reason:
                template.send_mail(rec.id)
                rec.state = 'rejected'
            else:
                raise UserError(_("Condition not met!, Need to Give the Reason for Rejection"))

    def state_waiting(self):
        template = self.env.ref('sales_circulation.demand_request_email_template')
        for rec in self:
            template.send_mail(rec.id)
            rec.state = 'waiting'

    def schedular_for_approval(self):
        demand_request = self.env['demand.request'].search([])
        for rec in demand_request:
            if rec.state == 'approved':
                if rec.selection_field == 'permanent' and rec.permanent_date == fields.Date.today():
                    agents = self.env['res.partner'].search([('id', '=', rec.Agent_id.id)])
                    for agent in agents:
                        if rec.update_agent_copies:
                            agent.update({
                                'n_q_zone': rec.update_agent_copies
                            })
                        elif rec.decrease_agent_copies:
                            agent.update({
                                'n_q_zone': rec.decrease_agent_copies
                            })
                    zone = self.env['res.partner'].search([('is_zone', '=', True)])
                    for z in zone.add_zones_to_line:
                        if z.cc_zone.id == rec.Agent_id.id:
                            if rec.update_agent_copies:
                                z.update({
                                    'newspaper_quantity_zone': rec.update_agent_copies
                                })
                            elif rec.decrease_agent_copies:
                                z.update({
                                    'newspaper_quantity_zone': rec.decrease_agent_copies
                                })

    # This method for redirect demand request based on users in this class defined the return action function

    @api.model
    def demand_request_approval(self):
        # here you can filter you records as you want
        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        field_segment_incharge = []
        for loop_1 in self.env['res.partner'].search([('hr_employee_id.user_id', '=', user_id.id)]):
            field_segment_incharge.append(loop_1.id)
        publications_incharge = []
        publications_incharge_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_2.id)]):
                    publications_incharge_list.append(agent.id)
                    if agent.id in publications_incharge_list:
                        publications_incharge.append(loop_1.user_partner_id.id)
                        publications_incharge.append(loop_2.user_partner_id.id)
                        publications_incharge.append(agent.id)
        circulation_incharge = []
        circulation_incharge_agent_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_3.id)]):
                        circulation_incharge_agent_list.append(agent.id)
                        if agent.id in circulation_incharge_agent_list:
                            circulation_incharge.append(loop_1.user_partner_id.id)
                            circulation_incharge.append(loop_2.user_partner_id.id)
                            circulation_incharge.append(loop_3.user_partner_id.id)
                            circulation_incharge.append(agent.id)
        unit_incharge = []
        unit_incharge_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for loop_4 in self.env['hr.employee'].search([('parent_id', '=', loop_3.id)]):
                        for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_4.id)]):
                            unit_incharge_list.append(agent.id)
                            if agent.id in unit_incharge_list:
                                unit_incharge.append(loop_1.user_partner_id.id)
                                unit_incharge.append(loop_2.user_partner_id.id)
                                unit_incharge.append(loop_3.user_partner_id.id)
                                unit_incharge.append(loop_4.user_partner_id.id)
                                unit_incharge.append(agent.id)
        regional_head = []
        regional_head_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for loop_4 in self.env['hr.employee'].search([('parent_id', '=', loop_3.id)]):
                        for loop_5 in self.env['hr.employee'].search([('parent_id', '=', loop_4.id)]):
                            for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_5.id)]):
                                regional_head_list.append(agent.id)
                                if agent.id in regional_head_list:
                                    regional_head.append(loop_1.user_partner_id.id)
                                    regional_head.append(loop_2.user_partner_id.id)
                                    regional_head.append(loop_3.user_partner_id.id)
                                    regional_head.append(loop_4.user_partner_id.id)
                                    regional_head.append(loop_5.user_partner_id.id)
                                    regional_head.append(agent.id)
        circulation_admin = []
        circulation_admin_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for loop_4 in self.env['hr.employee'].search([('parent_id', '=', loop_3.id)]):
                        for loop_5 in self.env['hr.employee'].search([('parent_id', '=', loop_4.id)]):
                            for loop_6 in self.env['hr.employee'].search([('parent_id', '=', loop_5.id)]):
                                for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_6.id)]):
                                    circulation_admin_list.append(agent.id)
                                    if agent.id in circulation_admin_list:
                                        circulation_admin.append(loop_1.user_partner_id.id)
                                        circulation_admin.append(loop_2.user_partner_id.id)
                                        circulation_admin.append(loop_3.user_partner_id.id)
                                        circulation_admin.append(loop_4.user_partner_id.id)
                                        circulation_admin.append(loop_5.user_partner_id.id)
                                        circulation_admin.append(loop_6.user_partner_id.id)
                                        circulation_admin.append(agent.id)
        circulation_head = []
        circulation_head_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for loop_4 in self.env['hr.employee'].search([('parent_id', '=', loop_3.id)]):
                        for loop_5 in self.env['hr.employee'].search([('parent_id', '=', loop_4.id)]):
                            for loop_6 in self.env['hr.employee'].search([('parent_id', '=', loop_5.id)]):
                                for loop_7 in self.env['hr.employee'].search([('parent_id', '=', loop_6.id)]):
                                    for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_7.id)]):
                                        circulation_head_list.append(agent.id)
                                        if agent.id in circulation_head_list:
                                            circulation_head.append(loop_1.user_partner_id.id)
                                            circulation_head.append(loop_2.user_partner_id.id)
                                            circulation_head.append(loop_3.user_partner_id.id)
                                            circulation_head.append(loop_4.user_partner_id.id)
                                            circulation_head.append(loop_5.user_partner_id.id)
                                            circulation_head.append(loop_6.user_partner_id.id)
                                            circulation_head.append(loop_7.user_partner_id.id)
                                            circulation_head.append(agent.id)
        super_admin = []
        super_admin_list = []
        for loop_1 in self.env['hr.employee'].search([('user_id', '=', user_id.id)]):
            for loop_2 in self.env['hr.employee'].search([('parent_id', '=', loop_1.id)]):
                for loop_3 in self.env['hr.employee'].search([('parent_id', '=', loop_2.id)]):
                    for loop_4 in self.env['hr.employee'].search([('parent_id', '=', loop_3.id)]):
                        for loop_5 in self.env['hr.employee'].search([('parent_id', '=', loop_4.id)]):
                            for loop_6 in self.env['hr.employee'].search([('parent_id', '=', loop_5.id)]):
                                for loop_7 in self.env['hr.employee'].search([('parent_id', '=', loop_6.id)]):
                                    for loop_8 in self.env['hr.employee'].search([('parent_id', '=', loop_7.id)]):
                                        for agent in self.env['res.partner'].search(
                                                [('hr_employee_id', '=', loop_8.id)]):
                                            super_admin_list.append(agent.id)
                                            if agent.id in super_admin_list:
                                                super_admin.append(loop_1.user_partner_id.id)
                                                super_admin.append(loop_2.user_partner_id.id)
                                                super_admin.append(loop_3.user_partner_id.id)
                                                super_admin.append(loop_4.user_partner_id.id)
                                                super_admin.append(loop_5.user_partner_id.id)
                                                super_admin.append(loop_6.user_partner_id.id)
                                                super_admin.append(loop_7.user_partner_id.id)
                                                super_admin.append(loop_8.user_partner_id.id)
                                                super_admin.append(agent.id)
        if super_admin:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', super_admin), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if circulation_head:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', circulation_head), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if circulation_admin:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', circulation_admin), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if regional_head:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', regional_head), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if unit_incharge:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', unit_incharge), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if circulation_incharge:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', circulation_incharge), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if publications_incharge:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', publications_incharge), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if field_segment_incharge:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', 'in', field_segment_incharge), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }
        if user_id.is_agent == True:
            return {
                'name': _('Demand Request Approval'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'demand.request',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('Agent_id', '=', user_id.partner_id.id), ('state', '=', 'waiting')],
                'views': [(self.env.ref('sales_circulation.demand_request_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.demand_request_tree').id or False, 'tree')],

            }


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('n_q_zone', 'f_q_zone', 'p_q_zone', 'v_q_zone', 'pr_q_zone', 'c_c_zone', 'o_q_zone')
    def update_quantity_in_zone(self):
        for rec in self:
            zone = self.env['res.partner'].search([('is_zone', '=', True)])
            for z in zone.add_zones_to_line:
                if z.cc_zone.id == rec.id:
                    z.update({
                        'newspaper_quantity_zone': rec.n_q_zone,
                        'Freebee_Quantity_zone': rec.f_q_zone,
                        'Postal_copies_zone': rec.p_q_zone,
                        'promotional_copies_zone': rec.pr_q_zone,
                        'corresspondents_copies_zone': rec.c_c_zone,
                        'office_copies_zone': rec.o_q_zone,
                        'voucher_copies_zone': rec.v_q_zone,
                    })
