# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    hide_return_btn = fields.Boolean(compute='_compute_hide_return_btn')

    @api.depends('partner_id', 'group_id')
    def _compute_hide_return_btn(self):
        self.hide_return_btn = False

        if self.group_id.sale_id and\
            self.group_id.sale_id.pricelist_id.campaign == 'cash_back':
                self.hide_return_btn = True

