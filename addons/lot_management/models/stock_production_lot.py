# -*- coding: utf-8 -*-

import datetime

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError, UserError

# upgrade16 ==> 'stock.lot' -> 'stock.lot'
class StocLot(models.Model):
    _inherit = 'stock.lot'
    
    name = fields.Char(compute='_compute_py_lot_fields', store=True, readonly=False)
    py_price_unit = fields.Float('Unit Price', digits='Product Price', compute='_compute_py_lot_fields', store=True, readonly=False)
    py_barcode = fields.Char('Barcode', compute='_compute_py_lot_fields', store=True, readonly=False)
    py_product_category = fields.Many2one(related='product_id.categ_id', string='Product Category', store=True)
    
    @api.onchange('expiration_date')
    def _onchange_expiration_date(self):
        if self.expiration_date:
            self.expiration_date = self.expiration_date.replace(hour=0, minute=0, second=0)
    
    @api.depends('product_id','expiration_date')
    def _compute_py_lot_fields(self):
        for record in self:
            if record.product_id and record.expiration_date:
                record.name = '%s-%s'%(record.expiration_date.strftime("%d/%m/%Y"), record.product_id.default_code)
                temp = datetime.datetime(1899, 12, 30)
                delta = record.expiration_date - temp
                date_excel = int(float(delta.days) + (float(delta.seconds) / 86400))
                record.py_barcode = '%s.%s'%(record.product_id.default_code, date_excel)
            elif record.product_id:
                record.py_price_unit = record.product_id.lst_price
            else:
                record.py_price_unit = 0.0
                record.py_barcode = ''
                    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            name = name.replace('ز', '.')
            args = [('py_barcode', operator, name)] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
    
    @api.model_create_multi
    def create(self, values):
        result = super(StocLot, self).create(values)
        for this in result:
            if this.py_price_unit == 0:
                raise ValidationError(_("The Price of Lot can't be 0"))
        return result

    def write(self, values):
        # upgrade16 ==> 'stock.lot' -> 'stock.lot'
        lot_ids = self.env['stock.lot'].search([])
        result = super(StocLot, self).write(values)
        for this in self:
            if this.py_price_unit == 0:
                raise ValidationError(_("The Price of Lot can't be 0"))
            if 'py_price_unit' in values and values['py_price_unit'] < this.py_price_unit and not self.env.user.has_group('base.group_system'):
                raise ValidationError(_("You can't change price to be less than the previous one"))
            if 'py_price_unit' in values and values['py_price_unit'] > this.py_price_unit and this.py_product_category.is_cosmetics:
                lot_to_update = lot_ids.filtered(lambda x: x.product_id == this.product_id)
                lot_to_update.py_price_unit = values['py_price_unit']
        return result
    
    _sql_constraints = [
    ('barcodeUniq', 'unique(py_barcode)', 'Barcode already exists!'),
    ]
