# -*- coding: utf-8 -*-

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        ret_list = []
        
        if self._context.get('tender_view'):
                for record in self:
                    name = str(record.name) + ' - ' + str(record.lst_price)
                    ret_list.append((record.id, name))
                return ret_list

        return super(ProductProduct, self).name_get()
# 