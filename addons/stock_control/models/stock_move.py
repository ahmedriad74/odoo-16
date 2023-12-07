# -*- coding: utf-8 -*-

from odoo import models, fields, _


class StockMove(models.Model):
    _inherit = "stock.move"

    #For split move by 20
    py_batch_source = fields.Char()
    stock_move_orderpoint_id = fields.Many2one('stock.move.orderpoint')

