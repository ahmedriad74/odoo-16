# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError


class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    py_quantity = fields.Integer("Product Quantity", required=True)
    py_quantity_unit = fields.Integer("Product Unit", required=True)

    @api.onchange('py_quantity','py_quantity_unit')
    def _onchange_py_quantity(self):
        strip_uom_factor = self.product_id.unit_factor if self.product_id else 1

        py_quantity = self.py_quantity
        py_quantity_unit = self.py_quantity_unit / strip_uom_factor
        self.quantity = py_quantity + py_quantity_unit
        product_uom_qty = self.move_id.product_uom_qty
        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        strip = round(self.py_quantity_unit / strip_uom_factor, rounding)
        rem = round(1 - (strip * strip_uom_factor), rounding)
        
        if abs(round(product_uom_qty - int(product_uom_qty) - strip, rounding)) == abs(rem):
            self.quantity = self.quantity + rem

        if self.quantity > product_uom_qty or self.quantity < 0:
            raise ValidationError(_('Please enter valid quantity'))


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)

        quantity = float(res['quantity'])
        py_quantity = py_quantity_unit= 0
        strip_uom_factor = stock_move.product_id.unit_factor if stock_move.product_id else 1
        py_quantity = int(quantity)
        py_quantity_unit = round((quantity - py_quantity) * strip_uom_factor, 0)

        res['py_quantity'] =  py_quantity
        res['py_quantity_unit'] = py_quantity_unit

        return res
    