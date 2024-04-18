from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.portal import CustomerPortal
# from odoo import api, fields, models


class SalesCirculationWebsite(http.Controller):

    # @http.route(['/agent_indent', '/agent_indent/page/<int:page>'], type='http', auth="public", website=True)
    # def agent_indent(self, page=1, search="", search_in="All", sortby="id"):
    @http.route(['/agent_indent'], type='http', auth="public", website=True)
    def agent_indent(self):
        user = request.env.uid
        user_id = request.env['res.users'].browse(user)
        values = {}
        agent_dict = []
        agent_indent = request.env['sale.order.line'].search([('agent_user_id', "=", user_id.id)])
        free_copies = 0
        agent_copies = 0
        postal_copies = 0
        voucher_copies = 0
        correspondents_copies = 0
        office_copies = 0
        promotional_copies = 0
        #
        for agent in agent_indent:
            free_copies += agent.free_copies
            agent_copies += agent.agent_copies
            postal_copies += agent.postal_copies
            voucher_copies += agent.voucher_copies
            correspondents_copies += agent.correspondents_copies
            office_copies += agent.office_copies
            promotional_copies += agent.promotional_copies

        for agent in agent_indent:
            agent_dict.append({
                # 'agent_code': agent.agent_code,
                'newspaper_date': agent.newspaper_date,
                'free_copies': agent.free_copies,
                'agent_copies': agent.agent_copies,
                'postal_copies': agent.postal_copies,
                'voucher_copies': agent.voucher_copies,
                'correspondents_copies': agent.correspondents_copies,
                'office_copies': agent.office_copies,
                'promotional_copies': agent.promotional_copies,
                'total_agent_copies': agent_copies,
                'total_free_copies': free_copies,
                'total_postal_copies': postal_copies,
                'total_voucher_copies': voucher_copies,
                'total_correspondents_copies': correspondents_copies,
                'total_office_copies': office_copies,
                'total_promotional_copies': promotional_copies,
            })
        #
        # search_list = {
        #     'All': {'label': 'All', 'input': 'All', 'domain': []},
        #     'Agent Code': {'label': 'Agent Code', 'input': 'Agent Code', 'domain': [('code', 'ilike', search)]}
        # }
        # sorted_list = {
        #     'id': {'label': 'ID Desc', 'order': 'id desc'},
        #     'name': {'label': 'Name', 'order': 'name'}
        # }
        #
        # default_order_by = sorted_list[sortby]['order']
        #
        # search_domain = search_list[search_in]['domain']
        # total_ident = agent_indent.search_count(search_domain)
        #
        # page_details = portal_pager(
        #     url='/agent_indent',
        #     total=total_ident,
        #     page=page,
        #     url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
        #     # step=5
        # )




        # indents = agent_indent.search([])
        # , limit = 5, order = default_order_by, offset = page_details['offset']
        values.update({
            # 'indent': indents,
            'agents': agent_dict,
            'page_name': 'agent_indent_list',
            # 'pager': page_details,
            # 'sortby': sortby,
            # 'searchbar_sortings': sorted_list,
            # 'search_in': search_in,
            # 'searchbar_inputs': search_list,
            # 'search': search,

        })

        return http.request.render('sales_circulation.agents_indent', values)

    @http.route('/agent_return', type='http', auth="public", website=True)
    def agent_return(self):
        user = request.env.uid
        user_id = request.env['res.users'].browse(user)
        values = {}
        agent_dict = []

        agent_return = request.env['contact.report'].search(
            [('agent', '=', user_id.partner_id.id), ('credit_note', '=', False),
             ('stock_picking_return.name', 'ilike', 'RET')])
        for returns in agent_return:
            agent_dict.append({
                'newspaper': returns.newspaper,
                'return_date': returns.return_date,
                'newspaper_return_qty': returns.newspaper_return_qty,
                'magazine_return_qty': returns.magazine_return_qty,
                'sp_return_qty': returns.sp_return_qty,
                'total_return': returns.total_return,
                'credit_note': returns.credit_note
            })
        values.update({
            'returns': agent_dict,
            'page_name': 'agent_return_list'
        })
        return http.request.render('sales_circulation.agents_return', values)


    # @http.route('/agents_invoice', type='http', auth="public", website=True)
    # def agents_invoice(self):
    #     user = request.env.uid
    #     user_id = request.env['res.users'].browse(user)
    #     values = {}
    #     agent_dict = []
    #
    #     agent_invoice = request.env['account.move'].search(
    #         [('partner_id', '=', user_id.partner_id.id), ('internal_order_bool', '=', True),
    #          ('move_type', '=', 'out_invoice')])
    #     for invoice in agent_invoice:
    #         status = ''
    #         state = ''
    #         if invoice.payment_state == 'not_paid':
    #             status += "Not Paid"
    #         elif invoice.payment_state == 'in_payment':
    #             status += "In Payment"
    #         elif invoice.payment_state == 'paid':
    #             status += "Paid"
    #         elif invoice.payment_state == 'partial':
    #             status += "Partially Paid"
    #         elif invoice.payment_state == 'reversed':
    #             status += "Reversed"
    #         elif invoice.payment_state == 'invoicing_legacy':
    #             status += "Invoicing App Legacy"
    #
    #         if invoice.state == 'draft':
    #             state += "Draft"
    #         elif invoice.state == 'posted':
    #             state += "Posted"
    #         elif invoice.state == 'cancel':
    #             state += "Cancelled"
    #
    #         agent_dict.append({
    #             'name': invoice.name,
    #             'invoice_date_due': invoice.invoice_date_due,
    #             'amount_untaxed_signed': invoice.amount_untaxed_signed,
    #             'amount_total_signed': invoice.amount_total_signed,
    #             'payment_state': status,
    #             'state': state,
    #             'amount_residual_signed': invoice.amount_residual_signed,
    #             'page_name': 'invoice',
    #         })
    #
    #     age_invoice_count = len(agent_dict)
    #     print(age_invoice_count)
    #     values.update({
    #         'invoices': agent_dict
    #     })
    #
    #     print(values)
    #
    #     return http.request.render('sales_circulation.agents_invoice', values)
#
    @http.route('/agent_deposit', type='http', auth="public", website=True)
    def agent_deposit(self):
        user = request.env.uid
        user_id = request.env['res.users'].browse(user)
        values = {}
        agent_dict = []
        agent_invoice = request.env['account.deposit'].sudo().search(
            [('partner_id', '=', user_id.partner_id.id), ('circulation', '=', True), ('status', '=', 'running')])
        for deposit in agent_invoice:
            agent_dict.append({
                'partner_id': deposit.partner_id.name,
                'deposit_amt': deposit.deposit_amt,
                'interest_percent': deposit.interest_percent
            })
        values.update({
            'deposits': agent_dict,
            'page_name': 'agent_deposit_list'
        })

        return http.request.render('sales_circulation.agent_deposit', values)

    @http.route(['/sales_circulation/indent/<model("sale.order.line"):indent_id>'], type='http', auth='public',
                website=True)
    def sales_circulation_indent(self, indent_id=1, **kwargs):

        values = {
            "indent": indent_id,
            'page_name': 'indent_from_view'
        }
        return http.request.render('sales_circulation.website_indent_form_view_portal', values)


class RetaPortalCount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(RetaPortalCount, self)._prepare_home_portal_values(counters)
        user = request.env.uid
        user_id = request.env['res.users'].browse(user)
        values['indent_count'] = request.env['sale.order.line'].search_count([('agent_user_id', "=", user_id.id)])
        values['deposit_count'] = request.env['account.deposit'].search_count(
            [('partner_id', '=', user_id.partner_id.id), ('circulation', '=', True), ('status', '=', 'running')])
        values['return_count'] = request.env['contact.report'].search_count(
            [('agent', '=', user_id.partner_id.id), ('credit_note', '=', False),
             ('stock_picking_return.name', 'ilike', 'RET')])

        return values
