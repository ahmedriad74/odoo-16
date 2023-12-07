# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    phone = fields.Char(index=True, related='partner_id.phone', readonly=True, store=True)