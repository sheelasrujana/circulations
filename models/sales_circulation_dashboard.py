from odoo import api, fields, models, tools, SUPERUSER_ID, _
from datetime import datetime, timedelta
import random
import calendar


class SalesCirculationDashboardData(models.Model):
    _name = 'sales.circulation.dashboard.data'

    unit_many2many_id = fields.Many2many(
        'res.partner',
        'partner_id',
        string='Units', domain=[('is_printing_unit', '=', True)]
    )
    from_date = fields.Date(string="Form Date")
    unit_name_string = fields.Char(string="Unit Name")
    from_date_string = fields.Char(string="From Date")
    to_date_string = fields.Char(string="To Date")

    # this method for compute the values of bar chart and pie chart and line chart in dashboard
    def get_invoice_line_vals(self, user_id):
        user_id = self.env['res.users'].search([('id', '=', int(user_id))])

        invoice_display_obj = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                               ('move_type', '=', 'out_invoice'),
                                                               ('state', '=', 'posted')])

        agent_list = []
        unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True), ('user_id', '=', user_id.id)])
        circulation_head_unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        if unit_ids:
            for unit in unit_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                agent_list.append(agents.cc_zone.id)
        else:
            for unit in circulation_head_unit_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                agent_list.append(agents.cc_zone.id)
        agent_name_list = []
        inv_total_amount_list = []
        inv_total_due_list = []
        amount_total_list = []
        amount_residual_list = []
        background_color = []
        border_color = []
        total_amount = 0.0
        total_amount_list = []
        total_due_amount = 0.0
        total_due_amount_list = []
        period_list = []
        for invoice in invoice_display_obj:
            if invoice.partner_id.id in agent_list:
                current_month = invoice.invoice_date.month
                month_name = calendar.month_name[current_month]
                current_year = invoice.invoice_date.year
                total_amount += invoice.amount_total
                total_due_amount += invoice.amount_residual
                agent_name_list.append(invoice.partner_id.name)
                inv_total_amount_list.append(round(total_amount, 2))
                inv_total_due_list.append(round(total_due_amount, 2))
                amount_total_list.append(invoice.amount_total)
                amount_residual_list.append(invoice.amount_residual)
                # for i in range(len(invoice_display_obj)):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                rgb_str = "#{:02X}{:02X}{:02X}".format(r, g, b)
                rgba_str = str(rgb_str) + 'ad'
                background_color.append(str(rgba_str))
                border_color.append(str(rgba_str))
            else:
                current_month = invoice.invoice_date.month
                month_name = calendar.month_name[current_month]
                current_year = invoice.invoice_date.year
                total_amount += invoice.amount_total
                total_due_amount += invoice.amount_residual
                agent_name_list.append(invoice.partner_id.name)
                inv_total_amount_list.append(round(total_amount, 2))
                inv_total_due_list.append(round(total_due_amount, 2))
                amount_total_list.append(invoice.amount_total)
                amount_residual_list.append(invoice.amount_residual)
                # for i in range(len(invoice_display_obj)):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                rgb_str = "#{:02X}{:02X}{:02X}".format(r, g, b)
                rgba_str = str(rgb_str) + 'ad'
                background_color.append(str(rgba_str))
                border_color.append(str(rgba_str))
            period_list.append(str(month_name) + ' ' + str(current_year))
            total_amount_list.append(round(total_amount, 2))
            total_due_amount_list.append(round(total_due_amount, 2))

        return {
            'period_list': period_list,
            'agent_name_list': agent_name_list,
            'inv_total_amount_list': total_amount_list,
            'inv_total_due_list': total_due_amount_list,
            'amount_total_list': amount_total_list,
            'amount_residual_list': amount_residual_list,
            'background_color': background_color,
            'border_color': border_color,
        }

    # @api.model
    def display_dashboard_vals(self, unt_name, from_date):
        list_new = []
        unit = ''
        from_date_1 = ''
        to_date = ''
        total_amount = 0.0
        total_due = 0.0
        account_move = self.env['account.move'].search([('invoice_date', '>=', unt_name),
                                                        ('invoice_date', '<=', from_date),
                                                        ('unit_id.name', '=', self.id)])
        return {
            'unit_name': self.id,
            'from_date': unt_name,
            'to_date': from_date
        }

    @api.model
    def get_display_data(self, unit_name, from_date, to_date):

        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        # agent_id = []
        # for loop_1 in self.env['res.partner'].search([('id', '=', user_id.partner_id.id)]):
        #     agent_id.append(loop_1.name)
        # print(agent_id, '####################################################')
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
                                        for agent in self.env['res.partner'].search([('hr_employee_id', '=', loop_8.id)]):
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
        demand_request_list = []
        payment_collections_total = 0.0
        total_amount = 0.0
        total_amount_due = 0.0
        total_commission_total = 0.0
        account_deposit_total_amount = 0.0
        account_deposit_total_amount_outstanding = 0.0
        invoice_lines = []
        week_indent_list = []
        if super_admin:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', super_admin),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', super_admin),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', super_admin)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', super_admin)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', super_admin)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
                # Get all records from the model
                today = fields.Date.context_today(self)
                today_new = datetime.today()
                start_day_of_week = today_new - timedelta(days=today.weekday())
                # Get the end day of the week
                end_day_of_week = start_day_of_week + timedelta(days=6)
                agent_week_indents_new = self.env['sale.order.line'].search(
                    [('order_id.internal_order', '=', True),
                     # ('order_id.state_duplicate', '=', 'sale'),
                     ('newspaper_date', '>=', start_day_of_week.date()),
                     ('newspaper_date', '<=', end_day_of_week.date()),
                     ('region_s', 'in', super_admin)])

                agent_week_dict = {}

                # Iterate through the records and organize them by agent and week date
                for indent in agent_week_indents_new:
                    agent_name = indent.region_s.name
                    week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                    # Initialize the agent if not present in the dictionary
                    agent_week_dict.setdefault(agent_name, {})

                    # Add the indent amount to the corresponding week date
                    agent_week_dict[agent_name].setdefault(week_date, 0)
                    agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif circulation_head:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', circulation_head),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', circulation_head),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', circulation_head)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', circulation_head)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', circulation_head)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', circulation_head)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif circulation_admin:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', circulation_admin),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', circulation_admin),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', circulation_admin)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', circulation_admin)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', circulation_admin)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', circulation_admin)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif regional_head:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', regional_head),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', regional_head),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', regional_head)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', regional_head)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', regional_head)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', regional_head)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif unit_incharge:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', unit_incharge),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', unit_incharge),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', unit_incharge)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', unit_incharge)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', unit_incharge)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', unit_incharge)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif circulation_incharge:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', circulation_incharge),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', circulation_incharge),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', circulation_incharge)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', circulation_incharge)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', circulation_incharge)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', circulation_incharge)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif publications_incharge:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', publications_incharge),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', publications_incharge),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', publications_incharge)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', publications_incharge)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', publications_incharge)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', publications_incharge)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies
        elif field_segment_incharge:
            demand_request = self.env['demand.request'].search([('Agent_id', 'in', field_segment_incharge),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', 'in', field_segment_incharge),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', 'in', field_segment_incharge)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', field_segment_incharge)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', 'in', field_segment_incharge)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', 'in', field_segment_incharge)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies

        elif user_id.is_agent == True:
            demand_request = self.env['demand.request'].search([('Agent_id', '=', user_id.partner_id.id),
                                                                ('state', '=', 'waiting')])
            for demand in demand_request:
                demand_request_list.append(demand.id)
            account_payment = self.env['account.payment'].search([('partner_id', '=', user_id.partner_id.id),
                                                                  ('state', '=', 'posted')])
            for pay in account_payment:
                payment_collections_total += pay.amount_company_currency_signed

            unit_account_move = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('state', '=', 'posted'),
                                                                 ('partner_id', '=', user_id.partner_id.id)])
            for agent in unit_account_move:
                total_amount += agent.amount_total_signed
                total_amount_due += agent.amount_residual_signed
                total_commission_total += agent.commission_total
            circulation_head_account_deposit = self.env['account.deposit'].search([
                                                                        ('partner_id', '=', user_id.partner_id.id)])
            for deposit in circulation_head_account_deposit:
                account_deposit_total_amount += deposit.deposit_amt
                account_deposit_total_amount_outstanding += deposit.total_outstanding
            unit_agents_account_move_lines = self.env['account.move'].search([('internal_order_bool', '=', True),
                                                                              ('move_type', '=', 'out_invoice'),
                                                                              ('state', '=', 'posted'),
                                                                          ('partner_id', '=', user_id.partner_id.id)])
            for invoice in unit_agents_account_move_lines:
                if invoice.amount_total != 0.00:
                    progress = round(invoice.amount_residual / invoice.amount_total * 100)
                else:
                    progress = 0
                invoice_lines.append({
                    'agent_name': invoice.partner_id.name,
                    'invoice_number': invoice.name,
                    'invoice_due_date': invoice.invoice_date_due,
                    'total_amount': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                    'progress': progress
                })
            # Get all records from the model
            today = fields.Date.context_today(self)
            today_new = datetime.today()
            start_day_of_week = today_new - timedelta(days=today.weekday())
            # Get the end day of the week
            end_day_of_week = start_day_of_week + timedelta(days=6)
            agent_week_indents_new = self.env['sale.order.line'].search(
                [('order_id.internal_order', '=', True),
                 # ('order_id.state_duplicate', '=', 'sale'),
                 ('newspaper_date', '>=', start_day_of_week.date()),
                 ('newspaper_date', '<=', end_day_of_week.date()),
                 ('region_s', '=', user_id.partner_id.id)])

            agent_week_dict = {}

            # Iterate through the records and organize them by agent and week date
            for indent in agent_week_indents_new:
                agent_name = indent.region_s.name
                week_date = indent.newspaper_date.strftime('%Y-%m-%d')

                # Initialize the agent if not present in the dictionary
                agent_week_dict.setdefault(agent_name, {})

                # Add the indent amount to the corresponding week date
                agent_week_dict[agent_name].setdefault(week_date, 0)
                agent_week_dict[agent_name][week_date] += indent.agent_copies

        current_day = datetime.today().strftime('%Y-%m-%d')
        previous_day = datetime.today() - timedelta(days=1)
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        partner_id = self.env['res.partner'].search([('id', '=', user_id.partner_id.id)])

        # Search for Internal orders created on the Today's unit and all units indent for circulation head
        indent_supplied = self.env['sale.order'].search([('internal_order', '=', True),
                                                         ('user_id', '=', user_id.id),
                                                         ('create_date', '>=', current_day + ' 00:00:00'),
                                                         ('create_date', '<', current_day + ' 23:59:59')])


        circulation_head_indent_supplied = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('create_date', '>=', current_day + ' 00:00:00'),
            ('create_date', '<', current_day + ' 23:59:59')])

        # Search for Internal  orders created on the previous day unit and all units indent for circulation head
        indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('user_id', '=', user_id.id),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])

        circulation_head_indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])

        # Loop for Internal orders created on the Today's unit and all units indent for circulation head
        total_copies_current_day = 0
        total_copies_previous_day = 0
        if indent_supplied:
            for so_line in indent_supplied.order_line:
                if so_line.product_id.is_newspaper == True:
                    total_copies_current_day += so_line.product_uom_qty

        else:
            if circulation_head_indent_supplied:
                for so_line in circulation_head_indent_supplied.order_line:
                    if so_line.product_id.is_newspaper == True:
                        total_copies_current_day += so_line.product_uom_qty

        # Loop for Internal  orders created on the previous day unit and all units indent for circulation head
        if indent_supplied_previous_day:
            for so_line in indent_supplied_previous_day.order_line:
                if so_line.product_id.is_newspaper == True:
                    total_copies_previous_day += so_line.product_uom_qty

        else:
            for so_line in circulation_head_indent_supplied_previous_day.order_line:
                if so_line.product_id.is_newspaper == True:
                    total_copies_previous_day += so_line.product_uom_qty

        # Search for unit agents and circulation head units agents
        agent_list = []
        unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True), ('user_id', '=', user_id.id)])
        circulation_head_unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])

        # Loop for unit agents
        if unit_ids:
            for unit in unit_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                agent_list.append(agents.cc_zone.id)

        # Loop for circulation head units agents
        else:
            for unit in circulation_head_unit_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                agent_list.append(agents.cc_zone.id)
        # Search for unit agents invoices


        # This loop for to search the unit agents payments
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

        # Loop for circulation units agents
        else:
            for unit in circulation_head__payment_unit_ids:
                for edition in unit.servie_regions:
                    for district in edition.district_o2m:
                        for zones in district.zone_o2m:
                            for agents in zones.add_zones_to_line:
                                head_agent_ids.append(agents.cc_zone.id)


        # Loop for circulation units agents payments
        # else:
        #     for pay in account_payment:
        #         if pay.partner_id.id in head_agent_ids:
        #             payment_collections_total += pay.amount_company_currency_signed

        transportation_bill = self.env['account.move'].search([('move_type', '=', 'in_invoice'),
                                                               ('is_transportation', '=', True),
                                                               ('state', '=', 'posted')])
        transportation_bill_total_amount = 0.0
        transportation_bill_total_amount_due = 0.0
        if transportation_bill:
            for vendor_bill in transportation_bill:
                transportation_bill_total_amount += vendor_bill.amount_total_signed
                transportation_bill_total_amount_due += vendor_bill.amount_residual

        # This Code For User To Get For Deposit amount & Outstanding Amount
        deposits_obj = self.env['account.deposit'].search(
            [('partner_id', '=', user_id.partner_id.id), ('circulation', '=', True), ('status', '=', 'running')])

        # Loop For Get For Deposit amount & Outstanding Amount for unit agents
        deposit_amt = 0.00
        outstanding_amt = 0.00
        if unit_agent_ids:
            for deposits in deposits_obj:
                if deposits.partner_id.id in unit_agent_ids:
                    deposit_amt += deposits.deposit_amt
                    outstanding_amt += deposits.total_outstanding

        # Loop For Get For Deposit amount & Outstanding Amount for circulation units agents
        else:
            for deposits in deposits_obj:
                if deposits.partner_id.id in head_agent_ids:
                    deposit_amt += deposits.deposit_amt
                    outstanding_amt += deposits.total_outstanding

        # This is for Agent invoice lines in table

        circulation_units_agents_head_agent_invoices = self.env['account.move'].search([
            ('internal_order_bool', '=', True),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')])
        # Loop for unit agents
        # if unit_account_move:
        #     for invoice in unit_agents_account_move_lines:
        #         if invoice.partner_id.id in agent_list:
        #             invoice_lines.append({
        #                 'agent_name': invoice.partner_id.name,
        #                 'invoice_number': invoice.name,
        #                 'invoice_due_date': invoice.invoice_date_due,
        #                 'total_amount': invoice.amount_total,
        #                 'amount_residual': invoice.amount_residual
        #             })
        # # Loop for unit agents
        # else:
        #     for invoice in circulation_units_agents_head_agent_invoices:
        #         invoice_lines.append({
        #             'agent_name': invoice.partner_id.name,
        #             'invoice_number': invoice.name,
        #             'invoice_due_date': invoice.invoice_date_due,
        #             'total_amount': invoice.amount_total,
        #             'amount_residual': invoice.amount_residual
        #         })

        # Search for demand request
        total_demand_request = 0
        demand_request = self.env['demand.request'].search([('state', '=', 'waiting')])
        # print()
        # print(user_id.partner_id.servie_regions.district_o2m.zone_o2m.add_zones_to_line.cc_zone)

        # Loop for units agents demand request
        if unit_agent_ids:
            for demand_agent in demand_request:
                if demand_agent.Agent_id.id in unit_agent_ids:
                    total_demand_request += 1

        # Loop for circulation units agents demand request
        else:
            if head_agent_ids:
                for demand_agent in demand_request:
                    if demand_agent.Agent_id.id in head_agent_ids:
                        total_demand_request += 1

        sale_order_lines = []
        unit_wise = self.env['sale.order'].search([('user_id', '=', user_id.id), ('internal_order', '=', True)])
        circulation_head_wise = self.env['sale.order'].search([('internal_order', '=', True)])
        if unit_wise:
            for lines in unit_wise.order_line:
                sale_order_lines.append({
                    'agent_name': lines.region_s.name,
                    'newspaper_date': lines.newspaper_date,
                    'agent_copies': lines.agent_copies,
                    'free_copies': lines.free_copies,
                    'postal_copies': lines.postal_copies,
                    'voucher_copies': lines.voucher_copies,
                    'promotional_copies': lines.promotional_copies,
                    'correspondents_copies': lines.correspondents_copies,
                    'office_copies': lines.office_copies,
                    'product_uom_qty': lines.product_uom_qty,
                })
        if not unit_wise:
            for lines in circulation_head_wise.order_line:
                sale_order_lines.append({
                    'agent_name': lines.region_s.name,
                    'newspaper_date': lines.newspaper_date,
                    'agent_copies': lines.agent_copies,
                    'free_copies': lines.free_copies,
                    'postal_copies': lines.postal_copies,
                    'voucher_copies': lines.voucher_copies,
                    'promotional_copies': lines.promotional_copies,
                    'correspondents_copies': lines.correspondents_copies,
                    'office_copies': lines.office_copies,
                    'product_uom_qty': lines.product_uom_qty,
                })

        # This Code For User To Get For Deposit amount & Outstanding Amount

        units_list = []
        unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        for unit in unit_ids:
            units_list.append({
                'id': unit.name
            })

        # This Method for current year total amount and total due of all the unit's for circulation head
        current_year = datetime.now().year

        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

        domain = [('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date),
                  ('internal_order_bool', '=', True)]
        records = self.env['account.move'].search(domain)
        invoice_unit_ids = self.env['res.partner'].search([('is_printing_unit', '=', True)])
        invoice_obj = []
        invoice_ids = []
        for unit in invoice_unit_ids:
            billed_amount = 0.0
            payment_amount = 0.0
            for invoice in records:
                account_move_obj = self.env['account.move'].search(
                    [('id', '=', invoice.id), ('unit_id', '=', unit.id)])
                account_payment_obj = self.env['account.payment'].search(
                    [('unit_id', '=', unit.id), ('ref', '=', invoice.name)])
                billed_amount += account_move_obj.amount_total
                payment_amount += account_payment_obj.amount_total
            if billed_amount != 0.00:
                progress = round(payment_amount / billed_amount * 100)
            else:
                progress = 0
            invoice_obj.append({
                'unit_name': unit.name,
                'billed_amount': "{0:.2f}".format(billed_amount),
                'payment_collected_amount': "{0:.2f}".format(payment_amount),
                'progress': progress
            })
        start_date_new = today - timedelta(days=today.weekday())
        date_range = [start_date_new + timedelta(days=x) for x in range(7)]

        return {
            'total_copies_current_day': total_copies_current_day,
            'total_copies_previous_day': total_copies_previous_day,
            'total_demand_request': len(demand_request_list),
            'total_amount': "{0:.2f}".format(total_amount),
            'total_amount_due': "{0:.2f}".format(total_amount_due),
            'payment_collections_total': "{0:.2f}".format(payment_collections_total),
            'total_commission_total': "{0:.2f}".format(total_commission_total),
            'account_deposit_total_amount': "{0:.2f}".format(account_deposit_total_amount),
            'account_deposit_total_amount_outstanding': "{0:.2f}".format(account_deposit_total_amount_outstanding),
            'transportation_bill_total_amount': "{0:.2f}".format(transportation_bill_total_amount),
            'transportation_bill_total_amount_due': "{0:.2f}".format(transportation_bill_total_amount_due),
            'indent_lines': sale_order_lines,
            'invoice_lines': invoice_lines,
            'invoice_obj': invoice_obj,
            'unit_many2many_id': units_list,
            'user': user_id.is_newsprint_unit,
            'agent_week_indent': agent_week_dict,
            'week_date_range' : date_range
        }

    def search_records_by_month(self, year, month):
        current_year = datetime.now().year

        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

        domain = [('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date), ('internal_order_bool', '=', True)]
        records = self.env['account.move'].search(domain)
        return records

# This class for redirect bills / invoices based on users in this class defined the return action function


class DashBoardAccountMoveBool(models.Model):
    _inherit = 'account.move'

    @api.model
    def agent_invoices(self):
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
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', super_admin), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif circulation_head:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', circulation_head), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif circulation_admin:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', circulation_admin), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif regional_head:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', regional_head), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif unit_incharge:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', unit_incharge), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif circulation_incharge:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', field_segment_incharge), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif publications_incharge:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', publications_incharge), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif field_segment_incharge:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', field_segment_incharge), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }
        elif user_id.is_agent == True:
            return {
                'name': _('Bills/Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'out_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', '=', user_id.partner_id.id), ('state', '=', 'posted'),
                           ('internal_order_bool', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_out_invoice_tree').id or False, 'tree')],

            }

    @api.model
    def vehicles_transportation_bill(self):
        # here you can filter you records as you want
        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        segment_incharge_units = [segment.id for segment in user_id.partner_id.segment_agents]
        vendor_list = [vendor.partner_id.id for vendor in
                       self.env['transport.vehicle'].search([('unit_id', '=', user_id.partner_id.id)])]
        segment_incharge_unit_users = [vendor.partner_id.id for units in segment_incharge_units
                                        for vendor in self.env['transport.vehicle']
                                       .search([('unit_id', '=', self.env['res.users'].browse(units).partner_id.id)])]
        if vendor_list:
            return {
                'name': _('Transportation Bills'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'in_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', vendor_list), ('state', '=', 'posted'),
                           ('is_transportation', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_in_invoice_bill_tree').id or False, 'tree')],

            }
        if segment_incharge_unit_users:
            return {
                'name': _('Transportation Bills'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'in_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', segment_incharge_unit_users), ('state', '=', 'posted'),
                           ('is_transportation', '=', True)],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_in_invoice_bill_tree').id or False, 'tree')],

            }
        if not vendor_list and segment_incharge_unit_users:
            return {
                'name': _('Transportation Bills'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'move_type': 'in_invoice',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('is_transportation', '=', True), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_move_form').id or False, 'form'),
                          (self.env.ref('account.view_in_invoice_bill_tree').id or False, 'tree')],

            }
# This class for redirect payment collections based on users in this class defined the return action function


class DashBoardAgentsPayments(models.Model):
    _description = "Agents Payments"
    _inherit = 'account.payment'

    @api.model
    def agents_account_payments(self):
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
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', super_admin), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if circulation_head:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', circulation_head), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if circulation_admin:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', circulation_admin), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if regional_head:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', regional_head), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if unit_incharge:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', unit_incharge), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if circulation_incharge:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', circulation_incharge), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if publications_incharge:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', publications_incharge), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if field_segment_incharge:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', field_segment_incharge), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }
        if user_id.is_agent == True:
            return {
                'name': _('Payment Collections'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'context': {'readonly_by_pass': True, 'check_domain': True},
                'domain': [('partner_id', 'in', field_segment_incharge), ('state', '=', 'posted')],
                'views': [(self.env.ref('account.view_account_payment_form').id or False, 'form'),
                          (self.env.ref('account.view_account_payment_tree').id or False, 'tree')],

            }

# This class for redirect only today's and yesterday's internal order's request based on users in this class defined the
# return action function


class DashBoardSaleOrder(models.Model):
    _inherit = 'sale.order'

    def today_indent_demand(self):
        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        current_day = datetime.today().strftime('%Y-%m-%d')
        previous_day = datetime.today() - timedelta(days=1)
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        partner_id = self.env['res.partner'].search([('id', '=', user_id.partner_id.id)])
        segment_incharge_units = [segment.id for segment in user_id.partner_id.segment_agents]
        # Search for Internal orders created on the Today's unit and all units indent for circulation head
        indent_supplied = self.env['sale.order'].search([('internal_order', '=', True),
                                                         ('create_date', '>=', current_day + ' 00:00:00'),
                                                         ('create_date', '<', current_day + ' 23:59:59')])
        unit_admin_indent_supplied = self.env['sale.order'].search([('internal_order', '=', True),
                                                                    ('user_id', '=', user_id.id),
                                                                    ('create_date', '>=', current_day + ' 00:00:00'),
                                                                    ('create_date', '<', current_day + ' 23:59:59')])
        segment_incharge_indent_supplied = self.env['sale.order'].search([('internal_order', '=', True),
                                                         ('user_id', 'in', segment_incharge_units),
                                                         ('create_date', '>=', current_day + ' 00:00:00'),
                                                         ('create_date', '<', current_day + ' 23:59:59')])

        circulation_head_indent_supplied = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('create_date', '>=', current_day + ' 00:00:00'),
            ('create_date', '<', current_day + ' 23:59:59')])

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

        # if segment_incharge_indent_supplied:
        #     return {
        #         'name': _('Today Indent Demand'),
        #         'type': 'ir.actions.act_window',
        #         'view_type': 'form',
        #         'view_mode': 'tree,form',
        #         'res_model': 'sale.order',
        #         'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
        #         'domain': [('id', '=', segment_incharge_indent_supplied.ids)],
        #         'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
        #                   (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],
        #
        #     }
        if super_admin:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', super_admin)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if circulation_head:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_head)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if circulation_admin:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_admin)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if regional_head:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', regional_head)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if unit_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('id', '=', indent_supplied.ids)],
                'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],

            }
        if circulation_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if publications_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', publications_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if field_segment_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', field_segment_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if unit_admin_indent_supplied:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('id', '=', unit_admin_indent_supplied.id)],
                'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],

            }
        if user_id.is_agent == True:
            return {
                'name': _('Today Indent Demand'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', '=', user_id.partner_id.id)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }

    def yesterday_indent_supplied(self):
        user = self.env.uid
        user_id = self.env['res.users'].browse(user)
        current_day = datetime.today().strftime('%Y-%m-%d')
        previous_day = datetime.today() - timedelta(days=1)
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        # Search for Internal  orders created on the previous day unit and all units indent for circulation head
        segment_incharge_units = [segment.id for segment in user_id.partner_id.segment_agents]
        indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])
        unit_admin_indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),('user_id', '=', user_id.id),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])

        segment_incharge_indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('user_id', 'in', segment_incharge_units),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])

        circulation_head_indent_supplied_previous_day = self.env['sale.order'].search([
            ('internal_order', '=', True),
            ('create_date', '>=', previous_day_str + ' 00:00:00'),
            ('create_date', '<', previous_day_str + ' 23:59:59')])

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

        # if indent_supplied_previous_day:
        #     return {
        #         'name': _('Yesterday Indent Supplied'),
        #         'type': 'ir.actions.act_window',
        #         'view_type': 'form',
        #         'view_mode': 'tree,form',
        #         'res_model': 'sale.order',
        #         'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
        #         'domain': [('id', '=', indent_supplied_previous_day.id)],
        #         'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
        #                   (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],
        #
        #     }
        #
        # if segment_incharge_indent_supplied_previous_day:
        #     return {
        #         'name': _('Yesterday Indent Supplied'),
        #         'type': 'ir.actions.act_window',
        #         'view_type': 'form',
        #         'view_mode': 'tree,form',
        #         'res_model': 'sale.order',
        #         'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
        #         'domain': [('id', '=', segment_incharge_indent_supplied_previous_day.ids)],
        #         'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
        #                   (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],
        #
        #     }
        if super_admin:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', super_admin)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if circulation_head:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_head)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if circulation_admin:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_admin)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if regional_head:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', regional_head)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if unit_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('id', '=', indent_supplied_previous_day.ids)],
                'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],

            }
        if circulation_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', circulation_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if publications_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', publications_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if field_segment_incharge:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', 'in', field_segment_incharge)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if user_id.is_agent == True:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('region_s', '=', user_id.partner_id.id)],
                'views': [(self.env.ref('sales_circulation.sale_order_line_tree_view').id or False, 'tree')],

            }
        if unit_admin_indent_supplied_previous_day:
            # for today in circulation_head_indent_supplied:
            return {
                'name': _('Yesterday Indent Supplied'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'context': {'readonly_by_pass': True, 'check_domain': True, 'create': False},
                'domain': [('id', '=', unit_admin_indent_supplied_previous_day.id)],
                'views': [(self.env.ref('sale.view_order_form').id or False, 'form'),
                          (self.env.ref('sales_circulation.view_internal_order_tree').id or False, 'tree')],

            }







