from odoo import http
from odoo.addons.account.controllers.portal import PortalAccount
from datetime import datetime,timedelta

from odoo.http import request


class PortalAccountInerit(PortalAccount):
    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = super(PortalAccountInerit, self).portal_my_invoices(page=1, date_begin=None, date_end=None, sortby=None,
                                                                  filterby=None)
        user_id = request.env.user

        date_obj = request.env['res.partner'].search([('id', '=', user_id.partner_id.id)])
        for follow_up in date_obj.unreconciled_aml_ids:
            days = ''
            current_date = datetime.now().date()
            remaining_days = (follow_up.date_maturity - current_date).days
            if remaining_days < 0:
                days += str(abs(remaining_days)) + " " + "days ago"
            elif remaining_days == 0:
                days += "Today"
            elif remaining_days > 0:
                days += "In" + " " + str(remaining_days) + " " + "days"

            values.qcontext.update({
                'remaining_days': days
            })
            print(days)
            print(values.qcontext)
        return values
