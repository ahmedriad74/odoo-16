# -*- coding: utf-8 -*-

import datetime

from odoo import models, fields, api, _ 

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []

            try:
                name = name.split('.')[0]
            except:
                pass

            args = [('default_code', '=', name)] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return result

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            
            try:
                name = name.split('.')[0]
            except:
                pass

            args = [('default_code', '=', name)] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return result
