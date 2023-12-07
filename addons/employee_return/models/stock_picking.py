# -*- coding: utf-8 -*-

from odoo import models, fields

class StockPicking(models.Model):
    _inherit = "stock.picking"

    return_sales_employee_id = fields.Many2one(
        string='Return Sales Employee',
        comodel_name='hr.employee',
        readonly=True
    )