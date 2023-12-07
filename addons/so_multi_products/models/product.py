# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # product_packaging = fields.Many2many('product.packaging', string='Package')
    # package_qty = fields.Float(string="Package QTY")
    py_box_product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=0)
    py_strip_product_uom_qty = fields.Float(string='Unit', digits='Product Unit of Measure', default=0)

    unit_price = fields.Float()
    available = fields.Text()

class SaleOreder(models.Model):
    _inherit = 'sale.order'

    def select_product(self):
        return {
                'name': _("Select Products"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'select.products',
                'target': 'new',
                'context': {
                    'default_pricelist_id': self.pricelist_id.id,
                    'default_warehouse_id': self.warehouse_id.id,
                }}
