# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    py_quantity = fields.Integer("Product Quantity", compute='_compute_py_quantity', readonly=False)
    py_quantity_unit = fields.Integer("Product Unit", compute='_compute_py_quantity', readonly=False)

    @api.depends('product_uom_qty')
    def _compute_py_quantity(self):
        for record in self:
            py_quantity = py_quantity_unit= 0
            strip_uom_factor = record.product_id.unit_factor if record.product_id else 1
            py_quantity = int(record.product_uom_qty)
            py_quantity_unit = round((record.product_uom_qty - py_quantity) * strip_uom_factor, 0)
            
            record.py_quantity = py_quantity
            record.py_quantity_unit = py_quantity_unit
    
    @api.onchange('py_quantity','py_quantity_unit')
    def _onchange_strip_box_product_uom_qty(self):
        strip_uom_factor = self.product_id.unit_factor if self.product_id else 1

        if self.product_id and self.product_id.unit_factor <= 0:
            message = 'Product %s can\'t have 0 unit factor.'%(self.product_id.name)
            raise UserError(_(message))

        if self.py_quantity_unit > strip_uom_factor - 1:
            message = 'Product can has only %s unit'%(strip_uom_factor - 1)
            raise ValidationError(_(message))

        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        strip = round(self.py_quantity_unit / strip_uom_factor, rounding)
        box = self.py_quantity
        self.product_uom_qty = strip + box
