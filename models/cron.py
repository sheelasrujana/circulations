from odoo import api, fields, models, tools, SUPERUSER_ID


class CronUser(models.Model):
    _inherit = 'ir.cron'
    user_id = fields.Many2one('res.users', 'Current User', compute='_compute_user')

    def _compute_user(self):
        for rec in self:
            rec.user_id = self._uid