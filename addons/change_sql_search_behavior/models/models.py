# -*- coding: utf-8 -*-

from odoo import models, api


class ProductInherit(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='=ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []

            args = [('name', '=ilike', name+'%')] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return result

