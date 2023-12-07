# -*- coding: utf-8 -*-

from odoo import models, fields

# HOLD
# class StockInventoryLine(models.Model):
#     _inherit = "stock.inventory.line"

#     def action_refresh_quantity(self):
        
#         filtered_lines = self.filtered(lambda l: l.state != 'done')
#         for line in filtered_lines:
#             if line.outdated:
#                 quants = self.env['stock.quant']._gather(line.product_id, line.location_id, lot_id=line.prod_lot_id, package_id=line.package_id, owner_id=line.partner_id, strict=True)
#                 if quants.exists():
#                     quantity = sum(quants.mapped('quantity'))
#                     if line.theoretical_qty != quantity:
#                         line.product_qty = line.product_qty - (line.theoretical_qty - quantity)
        
#         super().action_refresh_quantity()
                        

