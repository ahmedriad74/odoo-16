# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    def action_create_payments(self):
        if self.payment_difference < -2:
            raise ValidationError(_("Payment amount is higher than required."))
        return super().action_create_payments()
        
    @api.depends('full_amount','journal_id')
    def get_bank_charges_reg(self):
        super().get_bank_charges_reg()

        for payment in self:
            if payment.journal_id.type == "cash" and payment.journal_id.cash_difference_account_id and payment.payment_difference <= 2:
                payment.payment_difference_handling = 'reconcile'
                payment.writeoff_account_id = payment.journal_id.cash_difference_account_id.id
                
                if len(payment.line_ids.move_id):
                    payment.writeoff_label = ', '.join(payment.line_ids.move_id.mapped('name'))
                else:
                    payment.writeoff_label = payment.line_ids.move_id.name 
            else:
                payment.payment_difference_handling = 'open'
                payment.writeoff_account_id = False
                payment.writeoff_label = False
    
    # upgarde16
    # def _create_payment_vals_from_wizard(self):
    def _create_payment_vals_from_wizard(self, batch_result):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.journal_id.type == "cash" and self.journal_id.cash_difference_account_id and self.payment_difference <= 2:
            result['write_off_line_vals'] = {
                'name': 'Cash Difference on ' + str(self.writeoff_label),
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return result
        
