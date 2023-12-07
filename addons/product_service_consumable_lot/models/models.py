# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.onchange('type')
    def _onchange_product_type(self):
        for this in self:
            if this.type in ('consu','service'):
                this.tracking = 'none'
            else:
                this.tracking = 'lot'