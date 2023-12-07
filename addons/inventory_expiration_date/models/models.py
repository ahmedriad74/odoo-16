# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    expiration_date = fields.Datetime(related='lot_id.expiration_date', store=True, readonly=False)

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_create()
        res += ['expiration_date']
        return res

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()

        if 'inventory_quantity' in res \
            and not self.env.user.has_group('inventory_expiration_date.edit_inventory_quants'):
            res.remove('inventory_quantity')

        res += ['expiration_date']

        return res

    def update_qty(self, product_id=None, category=None):
        data = defaultdict(list)
        unique_lines = dict()
        self = self.search([])

        if category:
            self = self.filtered(lambda q: category in q.product_tmpl_id.categ_id.name
                                                and q.location_id.usage == 'internal'
                                                and q.product_tmpl_id.tracking == 'none')
        elif product_id:                                              
            self = self.filtered(lambda q: q.product_tmpl_id.id == product_id
                                        and q.location_id.usage == 'internal')

        for quant in self:
            key = f"{quant.location_id.id}_{quant.product_id}"
            data[key].append(quant.available_quantity)

        for unique_qunat in self:
            unique_key = f"{unique_qunat.location_id.id}_{unique_qunat.product_id}"

            if unique_key in unique_lines:
                unique_qunat.available_quantity = 0
            else:
                unique_lines[unique_key] = True
                unique_qunat.available_quantity = sum(data[unique_key])
