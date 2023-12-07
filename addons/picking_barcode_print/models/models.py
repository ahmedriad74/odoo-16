# -*- coding: utf-8 -*-

from odoo import models, fields, _


class StockMove(models.Model):
    _inherit = 'stock.move.line'
    
    barcode_flag = fields.Boolean(default=True, required=True)
    
    def print_barcode_once(self):
        for rec in self:
            rec.barcode_flag = False
