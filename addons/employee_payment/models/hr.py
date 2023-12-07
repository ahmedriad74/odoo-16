# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class hrEmployee(models.Model):

    _inherit = "hr.employee"

    is_casher = fields.Boolean('Casher')