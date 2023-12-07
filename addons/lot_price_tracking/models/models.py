# -*- coding: utf-8 -*-

from odoo import models, _
        
class StockLot(models.Model):
    _inherit = "stock.lot"

    def write(self, values):
        for rec in self:
            if values.get('py_price_unit'):
                rec.message_post(
                    body=_('The Unit Price has been Updated from %s to %s.') % (
                        rec.py_price_unit, values.get('py_price_unit')))

        res = super(StockLot, self).write(values)
        return res