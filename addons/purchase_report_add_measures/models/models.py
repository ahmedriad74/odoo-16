# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    unit_price = fields.Float('Uint price', readonly=True)
    
    discount_1 = fields.Float('Discount 1', readonly=True)
    discount_2 = fields.Float('Discount 2', readonly=True)
    levela_id = fields.Many2one('product.levela', 'Level A', readonly=True)
    item_comapny_id = fields.Many2one('product.item.company', 'Item company', readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + """, l.price_unit as unit_price
                                , l.percentage_discount_1 as discount_1, l.percentage_discount_2 as discount_2
                                , t.levela_id as levela_id, t.item_comapny_id as item_comapny_id"""

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + """, l.percentage_discount_1, l.percentage_discount_2, t.levela_id, t.item_comapny_id """
