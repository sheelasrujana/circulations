from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager



class WebsiteFormCirculation(http.Controller):

    @http.route('/create/demand', type='http', auth="public", website=True)
    def create_demand(self):
        user_id = request.env.user
        values = {
            'agent_name': user_id.name,
            'agent_copies': user_id.partner_id.n_q_zone
        }
        return http.request.render('sales_circulation.website_demand_request_form', values)

    @http.route('/send_for_approval', type='http', auth="public", website=True)
    def send_for_approval(self, **post):
        user_id = request.env.user

        values = {
            'Agent_id': user_id.partner_id.id,
            'Agent_copies': user_id.partner_id.n_q_zone,
            'selection_field': post.get('selection_field'),
            'permanent_date': post.get('permanent_date') if post.get('permanent_date') else datetime.now(),
            'specific_date': post.get('specific_date') if post.get('specific_date') else datetime.now(),
            'selection_update_agent_copies': post.get('selection_update_agent_copies'),
            'decrease_agent_copies': post.get('decrease_agent_copies'),
            'selection_additional_type': post.get('selection_additional_type'),
            'decrease_additional_copies': post.get('decrease_additional_copies'),
            'update_agent_copies': post.get('update_agent_copies') if post.get('update_agent_copies') else 0,
            'no_of_additional_copies': post.get('no_of_additional_copies') if post.get('no_of_additional_copies') else 0,

        }
        result = request.env['demand.request'].sudo().create(values)
        result.state_waiting()

        return http.request.render('sales_circulation.website_demand_request_thankyou', values)


    @http.route(['/demand/request','/demand/request/page/<int:page>'], type='http', auth="public", website=True)
    def demand_request(self,page=1):

        values = {}
        demand_req_dict = []
        demand_req_obj = request.env['demand.request'].search([])
        total_demands = demand_req_obj.search_count([])
        print(total_demands,"---------------")
        page_detail = pager(
            url = '/demand/request',
            total = total_demands,
            page = page,
            step = 15
        )
        demand_req_obj = request.env['demand.request'].search([], limit =15,offset = page_detail['offset'])

        for demand in demand_req_obj:
            if demand.selection_field == 'permanent':
                selection_field = 'Permanent'
            elif demand.selection_field == 'specific_date':
                selection_field = 'Specific date'

            if demand.demand_state == 'increase':
                demand_state = "Increase"
            elif demand.demand_state == 'decrease':
                demand_state = "Decrease"

            if demand.state == 'new':
                status = "New"
            elif demand.state == 'waiting':
                status = "Waiting for approval"
            elif demand.state == 'approved':
                status = "Approved"
            elif demand.state == 'rejected':
                status = "Rejected"

            demand_req_dict.append({
                'Agent_id': demand.Agent_id.name,
                'Agent_copies': demand.Agent_copies,
                'selection_field': selection_field,
                'specific_date': demand.specific_date.strftime("%m/%d/%Y"),
                'demand_changes': demand.demand_changes,
                'demand_state': demand_state,
                'status': status,

            })

            values.update({
                'demand_request':demand_req_dict,
                'page_name': 'demand_request',
                'pager': page_detail
            })
        return http.request.render('sales_circulation.demand_request', values)


class RetaPortalCount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(RetaPortalCount, self)._prepare_home_portal_values(counters)
        user = request.env.uid
        user_id = request.env['res.users'].browse(user)
        values['demand_count'] = request.env['demand.request'].search_count([])
        return values
