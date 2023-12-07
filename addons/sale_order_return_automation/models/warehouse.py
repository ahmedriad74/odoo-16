# -*- coding: utf-8 -*-

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_return_set_to_done = fields.Boolean(string="Is Return Set to Done")
    create_cn = fields.Boolean(string='Create CN?')
    validate_cn = fields.Boolean(string='Validate CN?')