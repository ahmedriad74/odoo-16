# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DawaaStockOnHand(models.Model):
    _name = 'dawaa.stock.on.hand'
    _description = 'Dawaa Stock on Hand'

    date = fields.Date('Date')
    product_id = fields.Many2one('product.product', string='Product')
    internal_ref = fields.Char(string='Ref.')
    levela_id = fields.Many2one('product.levela', string='Level A')
    location_id = fields.Many2one('stock.location', string='Location')
    # upgrade16 ==> 'stock.lot' -> 'stock.lot'
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number')
    lot_price = fields.Float('Lot Price')
    sale_price = fields.Float('Sale Price')
    current_month_on_hand = fields.Float('On Hand QTY (Current Month)')
    cuurent_month_available_qty = fields.Float('Available QTY (Current Month)')
    last_month_on_hand = fields.Float('On Hand QTY (Last Month)', default=0)
    last_month_available_qty = fields.Float('Available QTY (Last Moth)', default=0)
    total_sale = fields.Float('Toatl Sale')
    value = fields.Float('Value')

    def copy_stock_on_hand_date(self):
        vals = []
        data = {}
        stock_quant = self.env['stock.quant'].search([]).filtered(lambda q: q.location_id.usage == 'internal')

        for rec in stock_quant:
            total_sale = (rec.py_price_unit_lot if rec.product_id.tracking == 'lot' else rec.py_price_unit) * rec.quantity
            data = {
                'date': fields.Date.today(),
                'internal_ref': rec.internal_ref,
                'product_id': rec.product_id.id,
                'levela_id': rec.levela_id.id,
                'location_id': rec.location_id.id,
                'lot_id': rec.lot_id.id,
                'lot_price': rec.py_price_unit_lot,
                'sale_price': rec.py_price_unit,
                'current_month_on_hand': rec.quantity,
                'cuurent_month_available_qty': rec.available_quantity,
                'total_sale': total_sale,
                'value': rec.value
            }
            vals.append(data)

        self.create(vals)        