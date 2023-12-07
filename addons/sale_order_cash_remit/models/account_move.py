# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    order_payment_type = fields.Selection(
        string='Order Payment Type',
        selection=[('cash', 'Cash'), ('remit', 'أجل')],
        readonly=True
    )
    is_remit_valid = fields.Boolean(default=False)
    
    def set_remit_valid(self):
        self.is_remit_valid = True