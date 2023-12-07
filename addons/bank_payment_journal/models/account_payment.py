# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class account_payment(models.Model):
    _inherit = "account.payment"

    full_amount = fields.Monetary('Amount.', currency_field='currency_id')
    bank_charges = fields.Monetary(compute='get_bank_charges', default=0, currency_field='currency_id', string='Bank Charges', store=True)
    
    @api.depends('full_amount','journal_id')
    def get_bank_charges(self):
        for payment in self:
            amount = 0.0            
            if payment.journal_id.type == "bank" and payment.journal_id.bank_charges_account_id and payment.journal_id.charge_percentage > 0:
                amount = payment.full_amount
                payment.bank_charges = amount * (payment.journal_id.charge_percentage/100)
            else:
                payment.bank_charges = 0
    
    @api.onchange('bank_charges','full_amount')
    def onchange_bank_amount(self):
        if self.bank_charges > 0:
            amount = self.full_amount
            self.amount = amount - self.bank_charges
        else:
            self.amount = self.full_amount

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        if self.journal_id.type == "bank" and self.journal_id.bank_charges_account_id and self.bank_charges:
            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }
            default_line_name = self.env['account.move.line']._get_default_line_name(
                _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
                self.amount,
                self.currency_id,
                self.date,
                partner=self.partner_id,
            )
            write_off_line_vals = {
                    'name': 'Bank Fees on ' + str(default_line_name),
                    'amount': self.bank_charges,
                    'account_id': self.journal_id.bank_charges_account_id.id,
                }
        return super(account_payment, self)._prepare_move_line_default_vals(write_off_line_vals)
        
        
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    full_amount = fields.Monetary('Amount.', currency_field='currency_id', store=True, readonly=False, compute='_compute_full_amount')
    bank_charges = fields.Monetary(compute='get_bank_charges_reg', currency_field='currency_id', string='Bank Charges', store=True)
    
    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_full_amount(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.full_amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.full_amount = wizard.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id, wizard.payment_date)
                wizard.full_amount = amount_payment_currency

    @api.onchange('full_amount','journal_id', 'payment_date')
    def get_bank_charges_reg(self):
        for payment in self:
            bank_charges = 0.0
            amount = 0.0
            payment.bank_charges = bank_charges
            
            if payment.journal_id.type == "bank" and payment.journal_id.bank_charges_account_id and payment.journal_id.charge_percentage > 0:
                amount = payment.full_amount
                payment.bank_charges = amount * (payment.journal_id.charge_percentage/100)
                payment.amount = amount - payment.bank_charges
                payment.payment_difference = payment.bank_charges
                payment.payment_difference_handling = 'reconcile'
                payment.writeoff_account_id = payment.journal_id.bank_charges_account_id.id

                if len(payment.line_ids.move_id):
                    payment.writeoff_label = ', '.join(payment.line_ids.move_id.mapped('name'))
                else:
                    payment.writeoff_label = payment.line_ids.move_id.name 

                if (int(payment.source_amount) != int(payment.full_amount) 
                    or int(payment.source_amount) != int(payment.full_amount)) and payment.bank_charges != 0:
                    payment.payment_difference_handling = 'open'
            else:
                payment.amount = payment.full_amount

    # upgarde16
    # def _create_payment_vals_from_wizard(self):
    def _create_payment_vals_from_wizard(self, batch_result):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        
        result.update({
            'full_amount': self.full_amount,
            'bank_charges': self.bank_charges
        })

        if self.journal_id.type == "bank" and self.journal_id.bank_charges_account_id and self.journal_id.charge_percentage > 0:
            amount = self.full_amount
            self.bank_charges = amount * (self.journal_id.charge_percentage/100)
            self.amount = amount - self.bank_charges
            self.payment_difference = self.bank_charges
            self.payment_difference_handling = 'reconcile'
            self.writeoff_account_id = self.journal_id.bank_charges_account_id.id
            self.writeoff_label = self.line_ids.move_id.name        

        if self.bank_charges > 0 and not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            result['write_off_line_vals'] = {
                'name': 'Bank Fees on ' + str(self.writeoff_label),
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return result
