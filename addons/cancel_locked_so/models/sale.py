# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, values):
        if values.get('state') and self.state == 'done' and values['state'] == 'cancel': 
            raise ValidationError(_("Can't cancel locked sales order."))
            
        result = super(SaleOrder, self).write(values)
        return result
    