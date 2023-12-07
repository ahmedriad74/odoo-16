# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    cash_difference_account_id = fields.Many2one('account.account',string='Difference Account')
    
    @api.onchange('type')
    def _onchange_field_type_diff(self):
        if self.type != 'cash':
            self.cash_difference_account_id = False
    
    