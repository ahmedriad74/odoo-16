# -*- coding: utf-8 -*-

from odoo import models, fields


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    campaign = fields.Selection([('cash_back', 'Cash Back'), ('december_offer', 'Dec Offer')], string='Campaign')
    reward_product = fields.Many2one('product.product', string='Reward Product')