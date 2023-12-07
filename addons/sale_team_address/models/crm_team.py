# -*- coding: utf-8 -*-

import datetime

from odoo import models, fields, api, _ 

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    address_id = fields.Many2one('res.partner', string='Address')