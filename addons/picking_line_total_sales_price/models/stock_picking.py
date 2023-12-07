# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ro_total_lines_sale_price = fields.Float('Total Sale Price', compute='get_total_sale_price')

    @api.depends('move_line_ids')
    def get_total_sale_price(self):
        internal_pickings = self.filtered(lambda pick: pick.picking_type_code == 'internal')

        for picking in internal_pickings:
            ro_total_lines_sale_price = 0

            for move_line in picking.move_line_ids:
                ro_total_lines_sale_price += (move_line.lot_id.py_price_unit if move_line.product_id.tracking == 'lot' else move_line.product_id.list_price) * move_line.qty_done

            picking.ro_total_lines_sale_price = ro_total_lines_sale_price
            
        (self - internal_pickings).ro_total_lines_sale_price = 0
