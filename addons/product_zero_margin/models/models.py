# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    zero_margin = fields.Boolean('Zero Margin')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)

        if res.product_id.zero_margin:
            res.margin = 0
            res.margin_percent = 0
      
        return res
