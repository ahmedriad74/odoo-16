# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    end_date_consumption = fields.Date(string='End Consumption Date', readonly=True)