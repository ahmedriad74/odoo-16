# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    cash_back_amount = fields.Float()
    cash_back_order = fields.Char()
    got_offer = fields.Boolean(default=False)

