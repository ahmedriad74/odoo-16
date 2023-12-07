# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    order_payment_type = fields.Selection(
        string='Payment Type',
        selection=[('cash', 'Cash'), ('remit', 'أجل')],
        default='cash'
    )
    