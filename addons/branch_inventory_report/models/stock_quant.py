# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    ro_product_reference = fields.Char(related="product_tmpl_id.default_code")
    ro_product_name = fields.Char(related="product_tmpl_id.name")
    ro_product_price = fields.Float(compute='_compute_total_price')
    total_price = fields.Float('Total Price', compute='_compute_total_price')
    barcode = fields.Char(related='product_id.barcode')

    @api.depends('ro_product_price', 'quantity')
    def _compute_total_price(self):
        self.total_price = 0
        self.ro_product_price = 0

        for line in self:
            if line.product_tmpl_id.tracking == 'lot':
                product_lots = self.env['stock.lot'].search([('product_id', '=', line.product_id.id)])

                if product_lots:
                    highest = sorted(product_lots.mapped('py_price_unit'))[-1]
                    line.ro_product_price = max(highest, line.product_tmpl_id.list_price)
            else:
                line.ro_product_price = line.product_tmpl_id.list_price

            line.total_price = line.ro_product_price * line.quantity

    @api.model 
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'total_price' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_price = 0.0
                    for record in lines:
                        total_price += record.total_price
                    line['total_price'] = total_price
        return res
