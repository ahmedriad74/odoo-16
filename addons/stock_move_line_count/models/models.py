# -*- coding: utf-8 -*-

from odoo import models, fields


class StockInherit(models.Model):
    _inherit = 'stock.picking'

    moves_count = fields.Integer(string='Moves Count', compute='_count_moves', readonly=True)
    moves_line_count = fields.Integer(string='Moves Line Count', compute='_count_moves', readonly=True)
    start_line_print = fields.Integer(string='Start Line Print')

    def _count_moves(self):
        self.moves_count = self.env['stock.move'].search_count([('picking_id.id', '=', self.id)])
        self.moves_line_count = self.env['stock.move.line'].search_count([('picking_id.id', '=', self.id)])
