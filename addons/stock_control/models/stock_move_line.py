# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError
from datetime import datetime


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    py_lot_text = fields.Char('Lot')
    py_lot_unit_price = fields.Char('Lot Price')
    confirm_flag = fields.Boolean(string='Confirmed', default=False)
    picking_state = fields.Selection(related='picking_id.state')
    prod_lot_price = fields.Float(related='lot_id.py_price_unit', string='Lot Price')
    
    @api.onchange('py_lot_text')
    def _onchange_py_lot_text(self):
        if self.py_lot_text:
            lot_env = self.env['stock.lot']

            try:
                datetime_object = datetime.strptime(
                    self.py_lot_text, '%d/%m/%Y')
            except:
                raise UserError(_('Wrong Date Format.'))

            py_lot_text = (
                '%s-%s') % (datetime_object.strftime("%m/%d/%Y"), self.product_id.default_code)

            lot = lot_env.search(
                [('name', '=', py_lot_text), ('product_id', '=', self.product_id.id)])

            if len(lot):
                self.lot_id = lot
                self.expiration_date = lot.expiration_date
                self.py_lot_unit_price = lot.py_price_unit
            else:
                date_excel = datetime_object.toordinal() - datetime(2000, 1, 1).toordinal() + 1

                lot_id = lot_env.create({
                    'name': py_lot_text,
                    'product_id': self.product_id.id,
                    'expiration_date': datetime_object,
                    'py_barcode': '%s.%s' % (self.product_id.default_code, date_excel),
                    'py_price_unit': self.product_id.lst_price,
                    'company_id': self.company_id.id
                })

                self.lot_id = lot_id
                self.expiration_date = lot_id.expiration_date
                self.py_lot_unit_price = lot_id.py_price_unit

    @api.onchange('py_lot_unit_price')
    def _onchange_py_lot_unit_price(self):
        if self.lot_id:
            self.lot_id.py_price_unit = self.py_lot_unit_price

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.product_id:
            if self.picking_state == 'validate2'\
                and self._context.get('lock_lot_change')\
                and self.picking_code == 'internal'\
                and not self.env.user.has_group('base.group_system')\
                and self.location_dest_id.py_warehouse_id.is_main_wh:
                raise UserError(_('You are not allowed to change lots.'))
