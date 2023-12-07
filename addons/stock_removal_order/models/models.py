# -*- coding: utf-8 -*-

from odoo import models, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'felfo':
            return 'expiration_date, in_date, id'
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)
