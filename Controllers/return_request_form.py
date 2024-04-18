from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal


class ReturnRequestForm(http.Controller):


    @http.route('/return/request', type='http', auth="public", website=True)
    def return_request(self):
        user_id = request.env.user
        return_req_obj = request.env['return.request'].search([('agent_id', '=', user_id.partner_id.id),
                                                               ('state', '=', 'new')])

        values = {}
        ret_request = []
        for return_request in return_req_obj:
            status = ''
            if return_request.state == 'new':
                status += 'New'
            elif return_request.state == 'waiting':
                status += 'Waiting for approval'
            elif return_request.state == 'approved':
                status += 'Approved'
            elif return_request.state == 'news_paper_received':
                status += 'New Paper Received'
            elif return_request.state == 'credit_note_done':
                status += 'Credit Note Done'

            ret_request.append({
                'id': return_request.id,
                'agent_name': return_request.agent_id.name,
                'from_date': return_request.from_date.strftime("%d/%m/%Y"),
                'to_date': return_request.to_date.strftime("%d/%m/%Y"),
                'state': status,
            })
        values.update({
            'return_request': ret_request,
            'page_name': 'ret_request'
        })
        return http.request.render('sales_circulation.return_request', values)

    @http.route(['/return/request/form/<int:id>'], type='http', auth="public", website=True)
    def return_request_form(self, id):
        return_req_obj = request.env['return.request'].search([('id', '=', id)])
        values = {}
        return_request_line = []
        for return_request in return_req_obj:
            requests = []
            for return_line in return_request.return_request_line:
                product_type = ''
                return_type = ''
                if return_line.product_type == 'newspaper':
                    product_type += 'NewsPaper'
                elif return_line.product_type == 'magazine':
                    product_type += 'Magazine'

                if return_line.return_type == 'full_paper':
                    return_type += 'Full Paper'
                elif return_line.return_type == 'master_head':
                    return_type += 'Master Head'

                requests.append({
                    'id': return_line.id,
                    'date': return_line.date.strftime("%d/%m/%Y"),
                    'product_type': product_type,
                    'return_type': return_type,
                    'no_of_copies': return_line.no_of_copies,
                    'weight': return_line.weight,
                    'is_credit_done': return_line.is_credit_done
                })

            values.update({
                'id': return_request.id,
                'agent_name': return_request.agent_id.name,
                'products': return_request.product_news_paper_id.name,
                'from_date': return_request.from_date.strftime("%d/%m/%Y"),
                'to_date': return_request.to_date.strftime("%d/%m/%Y"),
                'state': return_request.state,
                'return_requests': requests,
                'return_request_line': return_request_line
            })
        return http.request.render('sales_circulation.website_return_request_form', values)


    @http.route('/return/request/submitted/<int:id>', type='http', auth="public", website=True)
    def return_request_submitted(self,id, **post):

        values = {
            'return_id': id,
            'is_credit_done': post.get('is_credit_done'),
            'date': post.get('date') if post.get('date') else datetime.now(),
            'product_type': post.get('product_type'),
            'return_type': post.get('return_type'),
            'no_of_copies': post.get('no_of_copies'),
            'weight': post.get('weight')
        }
        result = request.env['return.request.line'].create(values)
        result.send_return_request_mail()
        return http.request.render('sales_circulation.website_return_request_thankyou')

class RetaPortalCount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(RetaPortalCount, self)._prepare_home_portal_values(counters)
        user = request.env.uid
        values['ret_count'] = request.env['return.request'].search_count([])
        return values
