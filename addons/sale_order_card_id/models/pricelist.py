# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    id_required = fields.Boolean('Id Required')