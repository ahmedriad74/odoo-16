# -*- coding: utf-8 -*-

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    parent_warehouse_id = fields.Many2one(
        string='Parent Stock Warehouse',
        comodel_name='stock.warehouse'
    )
