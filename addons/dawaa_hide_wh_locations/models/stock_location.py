# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    hide_location = fields.Boolean('Hide Location') 
