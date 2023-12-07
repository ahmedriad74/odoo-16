# -*- coding: utf-8 -*-

from odoo import models

class Product(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        result = super(Product, self).name_get()
        new_result = []

        if self._context.get('rfq_product'):
            for product_set in result:
                product_id = product_set[0]
                product_name = product_set[1]
                product = self.browse(product_id)
                new_product_name = f'{product_name} [({str(product.list_price)})]'
                new_result.append((product_id, new_product_name))

            return new_result

        return result
        