# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmTeam(models.Model):
    _inherit = "crm.team"
    
    area = fields.Selection(
        string='Area',
        selection=[('alex', 'Alexandria'), ('tanta', 'Tanta')]
    )
