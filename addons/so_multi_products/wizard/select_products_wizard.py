# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, SUPERUSER_ID
import itertools

class SelectProducts(models.TransientModel):
    _name = 'select.products'
    _description = 'Select Products'

    pricelist_id = fields.Many2one('product.pricelist')
    warehouse_id = fields.Many2one('stock.warehouse')
    product_ids = fields.Many2many('product.product', 'product_select_product_rel', 'product_id', 'select_id', string='Products')
    
    @api.onchange('product_ids')
    def update_price_unit(self):
        for this in self:
            if this.pricelist_id and this.product_ids:
                for p_id, p in zip (self.product_ids.ids,self.product_ids):
                        qty_list = self.env['product.pricelist.item'].search([('pricelist_id', '=', this.pricelist_id.id),('product_id', '=', p_id)]).sorted(lambda x:x.min_quantity)
                        p.unit_price = qty_list[0].fixed_price if len(qty_list) > 0 else p.lst_price                   
                        location = this.warehouse_id.lot_stock_id
                        strip_uom_factor = p.unit_factor if p else 1
                        quants_all = p.stock_quant_ids.filtered(lambda q: 
                                                                    (q.location_id.usage == 'internal' or
                                                                    (q.location_id.usage == 'transit' and q.location_id.company_id)) and
                                                                    (q.location_id == location)
                                                                )

                        qty_in_all_lot = sum(quants_all.mapped('available_quantity'))
                        remain_qty_in_all_lot = (qty_in_all_lot - int(qty_in_all_lot)) * strip_uom_factor
                        p.available = '%s Qty\n%s Unit'% (int(qty_in_all_lot), round(remain_qty_in_all_lot, 0))

    def select_products(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_id', False))

        for product in self.product_ids:
            if product.py_box_product_uom_qty > 0 or product.py_strip_product_uom_qty > 0:
                order_line = self.env['sale.order.line'].create({
                        'product_id': product.id,
                        'py_box_product_uom_qty': product.py_box_product_uom_qty,
                        'py_strip_product_uom_qty': product.py_strip_product_uom_qty,
                        'product_uom': product.uom_id.id,
                        'order_id': order_id.id,
                    })
                order_line._onchange_strip_box_product_uom_qty()

            product.with_user(SUPERUSER_ID).write({
                'py_box_product_uom_qty': 0,
                'py_strip_product_uom_qty': 0,
                'unit_price': 0,
                'available': False,
            })
