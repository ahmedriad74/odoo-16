# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char(copy=False)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['ref'] = self.env['ir.sequence'].next_by_code('res.partner.sequence')
        return super().create(vals)
