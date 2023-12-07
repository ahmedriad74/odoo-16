# -*- coding: utf-8 -*-

from odoo import models, fields, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_sale_order_count = fields.Integer('Sale Order Count', related='partner_id.sale_order_count')
    partner_tag_ids = fields.Many2many('res.partner.category', string='Partner Tags', related='partner_id.category_id')