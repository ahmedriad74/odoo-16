# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json

class ProductTemplate(models.Model):
    _inherit = "product.template"

    higest_lot_price = fields.Float(compute='_compute_higest_lot_price', string='Highest Lot Price')

    @api.depends('tracking')
    def _compute_higest_lot_price(self):
        self.higest_lot_price = 0

        for product in self:            
            if product.tracking == 'lot':
                product_product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                # upgrade16 ==> 'stock.lot' -> 'stock.lot'
                product_lots = self.env['stock.lot'].search([('product_id', '=', product_product.id)])

                if product_lots:
                    product.higest_lot_price = sorted(product_lots.mapped('py_price_unit'))[-1]

                    if product.higest_lot_price > product.list_price:
                        product.list_price = product.higest_lot_price
