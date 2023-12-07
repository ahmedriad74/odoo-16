# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_shortfall = fields.Boolean('نواقص')
    is_cosmo_shortfall = fields.Boolean('cosmo نواقص')
