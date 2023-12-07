# -*- coding: utf-8 -*-

from odoo import models, fields, _

class StockRoute(models.Model):
    _inherit = 'stock.route'
    
    used_warehouse_id = fields.Many2one(
        string='Used Warehouse',
        comodel_name='stock.warehouse'
    )
    py_is_buy_route = fields.Boolean(string='Buy Route')
    py_is_reorder_route = fields.Boolean(string='Reorder Route')
