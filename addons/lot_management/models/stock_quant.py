# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    available_quantity = fields.Float(store=True)
    py_price_unit = fields.Float('Sale Price', related="product_id.list_price", store=True, group_operator=False)
    py_price_unit_lot = fields.Float('Lot Sale Price', related="lot_id.py_price_unit", store=True, group_operator=False)
    ro_total_sale_price = fields.Float('Total Sale', compute='get_total_sale_price')

    @api.depends('py_price_unit', 'py_price_unit_lot', 'inventory_quantity')
    def get_total_sale_price(self):
        for quant in self:
            quant.ro_total_sale_price = (quant.py_price_unit_lot if quant.product_id.tracking == 'lot' else quant.py_price_unit) * quant.inventory_quantity

