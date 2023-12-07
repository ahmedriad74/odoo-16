# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(index=True, copy=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            args = [('phone', operator, name)] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return result

    @api.constrains('phone')
    def _check_phone_number(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                    raise ValidationError(_("Phone only accept numbers"))
                    
    @api.model_create_multi
    def create(self, values):
        for value in values:
            if value.get('phone'):
                value['phone'] = value['phone'].replace('+2','').replace(' ','')

            result = super().create(values)
        return result
    
    def write(self, values):
        if values.get('phone'):
            values['phone'] = values['phone'].replace('+2','').replace(' ','')
            
        result = super().write(values)    
        return result
        
