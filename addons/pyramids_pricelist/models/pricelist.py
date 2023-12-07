# -*- coding: utf-8 -*-

import datetime

from odoo import models, fields, api, _ 

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    is_contract = fields.Boolean(string='Contract', default=True)
    is_depend_on_cost = fields.Boolean(string='Depend On Cost', default=False)
    free_products_by_margin = fields.Boolean('Free Products by Margin')
    product_cost = fields.Boolean('Product Cost')
