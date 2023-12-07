# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    internal_ref = fields.Char(related='product_id.default_code', store=True, readonly=False)
    product_name = fields.Char(related='product_id.name', store=True, readonly=False)
    levela_id = fields.Many2one(related='product_id.levela_id', store=True, readonly=False)
    item_comapny_id = fields.Many2one(related='product_id.item_comapny_id', store=True, readonly=False)
    vendor_id = fields.Many2one(related='product_id.vendor_id', store=True)

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_create()
        res += ['internal_ref']
        res += ['product_name']
        res += ['levela_id']
        res += ['item_comapny_id']
        res += ['vendor_id']
        res += ['ro_total_sale_price']

        return res

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()
        res += ['internal_ref']
        res += ['product_name']
        res += ['levela_id']
        res += ['item_comapny_id']
        res += ['vendor_id']
        res += ['ro_total_sale_price']

        return res
