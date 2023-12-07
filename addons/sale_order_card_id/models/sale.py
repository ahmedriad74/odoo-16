# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    id_required = fields.Boolean('Id Required', related='pricelist_id.id_required')
    card_id = fields.Char('Id')