# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_cosmetics = fields.Boolean("Is Cosmo")    
    is_dawaa = fields.Boolean("Is Dawaa")    
    lot_be_highest_price = fields.Boolean()

    def update_lot_to_high_price(self, context=None):
        if context == 'cron':
            self = self.search([])
            
        for categ in self:
            if categ.lot_be_highest_price:
                # upgrade16 ==> 'stock.lot' -> 'stock.lot'
                category_lots = self.env['stock.lot'].search([('py_product_category', '=', categ.id)])
                products = category_lots.mapped('product_id')

                for product in products:
                    lots_to_update = category_lots.filtered(lambda x:x.product_id == product).sorted('py_price_unit')

                    if len(list(dict.fromkeys(lots_to_update.mapped('py_price_unit')))) > 1:                    
                        lots_to_update.filtered(lambda x:x.py_price_unit != lots_to_update[-1].py_price_unit).py_price_unit = lots_to_update[-1].py_price_unit
