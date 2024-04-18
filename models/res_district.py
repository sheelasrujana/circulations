import re
import logging
from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.exceptions import UserError


class CountryState(models.Model):
    _description = "State District"
    _name = 'res.state.district'
    _order = 'code'

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    name = fields.Char(string='District Name', required=True,
               help='Administrative divisions of a state. E.g. Fed. State, Departement, Canton')
    code = fields.Char(string='District Code', help='The district code.', required=True)