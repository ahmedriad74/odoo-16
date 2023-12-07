# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError

class Resusers(models.Model):
    _inherit = 'res.users'

    def str_to_int(self,name):
        name = name.lower()
        output = ''
        for character in name:
            number = ord(character) - 96
            output += str(abs(number))
        return output

    def copy(self, default=None):
        """
            Create a new record in ModelName model from existing one
            @param default: dict which contains the values to be override during
            copy of object
    
            @return: returns a id of newly created record
        """
        self.ensure_one()
        default = dict(default or {})
        if ('phone' not in default) and ('partner_id' not in default):
            default['phone'] = self.str_to_int(self.login)

        result = super().copy(default)
        return result
    
    @api.model_create_multi
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        values['phone'] = self.str_to_int(values['login'])

        result = super().create(values)
        return result
  