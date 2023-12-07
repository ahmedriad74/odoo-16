# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo import exceptions

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super(StockReturnPicking, self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        res['qty_conf'] = res['quantity']  
        return res

    def create_returns(self):
        new = super(StockReturnPicking, self).create_returns()
        for rec in self:
            for move in rec.product_return_moves:
                if move.qty_conf < 0 or move.qty_conf < move.quantity:
                    raise exceptions.ValidationError(_('Cannot make this step'))
        return new

class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    qty_conf = fields.Float('qty_conf', readonly=True)
