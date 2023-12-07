# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(copy=False)

    @api.model_create_multi
    def create(self, vals):
        vals[0]['default_code'] = self.env['ir.sequence'].next_by_code('product.template.sequence')
        return super().create(vals)

