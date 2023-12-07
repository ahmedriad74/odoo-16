# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stockQuant(models.Model):
    _inherit = 'stock.quant'

    rate = fields.Float('Rate', compute='_compute_rate')

    @api.depends('product_id')
    def _compute_rate(self):
        self.rate = 0
        dic = {}

        self.env.cr.execute("""
            select scr.location_id, scr.product_id, scr.rate
            from stock_quant q, stock_consumption_rate scr
            where q.product_id = scr.product_id
            and q.location_id = scr.location_id
            and scr.product_id in {}
            """.format(tuple(self.product_id.ids)+ (0,)))

        data_list = self._cr.dictfetchall()

        for data in data_list:
            key = f"{data['product_id']}_{data['location_id']}"
            dic[key] = data['rate']

        for line in self:
            new_key = f"{line.product_id.id}_{line.location_id.id}"

            if new_key in dic:
                line.rate = dic[new_key]

