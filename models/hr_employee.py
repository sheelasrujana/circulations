from odoo import fields, api, models, _
from datetime import datetime, timedelta


class HrEmployeeCirculation(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals_list):
        res = super(HrEmployeeCirculation, self).create(vals_list)

        uesr_idd = self.env['res.users'].search([('id', '=', res['user_id'].id)])

        uesr_idd.hr_employee_cirulation_agent = res['id']
        return res