import logging

from odoo import models, fields, api,_
from odoo import tools
from datetime import datetime
from num2words import num2words


from odoo.exceptions import UserError, ValidationError


class StockPayment(models.Model):
        _inherit="account.payment"

        is_document = fields.Boolean()
        partner_id = fields.Many2one(
                comodel_name='res.partner',
                string="Customer/Vendor",
                store=True, readonly=False, ondelete='restrict',
                check_company=True)
        destination_account_id = fields.Many2one(
                comodel_name='account.account',
                string='Destination Account',
                store=True, readonly=False,
                domain="[('company_id', '=', company_id)]",
                check_company=True)
        journal = fields.Char(compute='compute_flag')
        post_type = fields.Selection([
               ('single', 'Single Account'), 
               ('multi', 'Multiple Accounts')],
                default='single', string='Post Difference In To')
        writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_id', string='Write Off Accounts')
        numinwords = fields.Char(string='Total in words',compute='_getnumbernew',store=False)

        @api.depends('payment_type')
        def compute_flag(self):
            for rec in self:
                if rec.payment_type == 'inbound':
                    rec.journal = 'in'
                elif rec.payment_type == 'outbound':
                    rec.journal = 'out'

        @api.onchange('payment_type')
        def _check_on_post_type(self):
                for rec in self:
                    rec.post_type = 'single'

        @api.depends('is_internal_transfer')
        def _compute_destination_account_id(self):
                for pay in self:
                        if pay.is_internal_transfer:
                                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id

        @api.depends('amount')
        def _getnumbernew(self):
                for rec in self:
                        numinwords = num2words(float(rec.amount), lang='ar',)
                        numinwords = ('مبلغ وقدره {} جنيه مصري فقط لاغير').format(numinwords)
                        rec.numinwords = numinwords

        @api.onchange('date')
        def _compute_company_date(self):
                self.company_id = self.env.user.company_id.id

        @api.onchange('writeoff_multi_acc_ids')
        def _compute_multi_account(self):
                total = 0
                if self.writeoff_multi_acc_ids:
                        for line in self.writeoff_multi_acc_ids:
                                total += line.amount
                self.amount = total

        def _prepare_move_line_default_vals(self, write_off_line_vals=None):
                ''' Prepare the dictionary to create the default account.move.lines for the current payment.
                :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
                * amount:       The amount to be added to the counterpart amount.
                * name:         The label to set on the line.
                * account_id:   The account on which create the write-off.
                :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
                '''
                self.ensure_one()
                if self.payment_method_code not in  ('received_third_check','issue_check','delivered_third_check'):
                        write_off_line_vals = write_off_line_vals or {}
                        # upgrade16 ==> 'journal_id.payment_credit_account_id' --> 'outstanding_account_id'
                        # if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
                        if not self.outstanding_account_id:
                                raise UserError(_(
                                        "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                                        self.journal_id.display_name))

                        # Compute amounts.
                        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

                        if self.payment_type == 'inbound':
                                # Receive money.
                                liquidity_amount_currency = self.amount
                        elif self.payment_type == 'outbound':
                                # Send money.
                                liquidity_amount_currency = -self.amount
                                write_off_amount_currency *= -1
                        else:
                                liquidity_amount_currency = write_off_amount_currency = 0.0

                        write_off_balance = self.currency_id._convert(
                                write_off_amount_currency,
                                self.company_id.currency_id,
                                self.company_id,
                                self.date,
                        )
                        liquidity_balance = self.currency_id._convert(
                                liquidity_amount_currency,
                                self.company_id.currency_id,
                                self.company_id,
                                self.date,
                        )
                        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
                        counterpart_balance = -liquidity_balance - write_off_balance
                        currency_id = self.currency_id.id

                        if self.is_internal_transfer:
                                if self.payment_type == 'inbound':
                                        liquidity_line_name = _('Transfer to %s', self.journal_id.name)
                                else: # payment.payment_type == 'outbound':
                                        liquidity_line_name = _('Transfer from %s', self.journal_id.name)
                        else:
                                liquidity_line_name = self.payment_reference

                        # Compute a default label to set on the journal items.
                        # upgrade16
                        # payment_display_name = {
                        #         'outbound-customer': _("Customer Reimbursement"),
                        #         'inbound-customer': _("Customer Payment"),
                        #         'outbound-supplier': _("Vendor Payment"),
                        #         'inbound-supplier': _("Vendor Reimbursement"),
                        # }

                        # default_line_name = self.env['account.move.line']._get_default_line_name(
                        #         _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
                        #         self.amount,
                        #         self.currency_id,
                        #         self.date,
                        #         partner=self.partner_id,
                        # )
                        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
                        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

                        if self.post_type == 'single':
                                line_vals_list = [
                                        # Liquidity line.
                                        {
                                                'name': liquidity_line_name,
                                                'date_maturity': self.date,
                                                'amount_currency': liquidity_amount_currency,
                                                'currency_id': currency_id,
                                                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                                                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                                                'partner_id': self.partner_id.id,
                                                'account_id': self.outstanding_account_id.id
                                        },
                                        # Receivable / Payable.
                                        {
                                                'name': counterpart_line_name,
                                                'date_maturity': self.date,
                                                'amount_currency': counterpart_amount_currency,
                                                'currency_id': currency_id,
                                                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                                                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                                                'partner_id': self.partner_id.id,
                                                'account_id': self.destination_account_id.id,
                                        },
                                ]
                        elif self.post_type == 'multi':
                                line_vals_list = [
                                        # Liquidity line.
                                        {
                                        'name': liquidity_line_name,
                                        'date_maturity': self.date,
                                        'amount_currency': liquidity_amount_currency,
                                        'currency_id': currency_id,
                                        'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                                        'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': self.outstanding_account_id.id
                                        }]
                                for account_line in self.writeoff_multi_acc_ids:
                                        line_vals_list.append(
                                        # Receivable / Payable.
                                        {
                                                'name': counterpart_line_name,
                                                'date_maturity': self.date,
                                                'amount_currency': account_line.amount,
                                                'currency_id': currency_id,
                                                'debit': account_line.amount if liquidity_balance < 0.0 else 0.0,
                                                'credit': -account_line.amount if liquidity_balance > 0.0 else 0.0,
                                                'partner_id': self.partner_id.id,
                                                'account_id': account_line.writeoff_account_id.id,
                                                'analytic_account_id': account_line.analytic_account_id.id,
                                                # upgrade16
                                                # 'analytic_tag_ids': [(4, tag, None) for tag in account_line.analytic_tag_ids.ids],
                                                'analytic_distribution': account_line.analytic_distribution,
                                        })

                        if not self.currency_id.is_zero(write_off_amount_currency):
                                # Write-off line.
                                line_vals_list.append({
                                        'name': write_off_line_vals.get('name'),
                                        'amount_currency': write_off_amount_currency,
                                        'currency_id': currency_id,
                                        'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                                        'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': write_off_line_vals.get('account_id'),
                                })
                                
                        return line_vals_list
                else:
                        write_off_line_vals = write_off_line_vals or {}

                        if not self.outstanding_account_id:
                                raise UserError(_(
                                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                                self.journal_id.display_name))

                        # Compute amounts.
                        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)
                        
                        if self.payment_type == 'inbound':
                                # Receive money.
                                liquidity_amount_currency = self.amount
                        elif self.payment_type == 'outbound':
                                # Send money.
                                liquidity_amount_currency = -self.amount
                                write_off_amount_currency *= -1
                        else:
                                liquidity_amount_currency = write_off_amount_currency = 0.0

                        write_off_balance = self.currency_id._convert(
                                write_off_amount_currency,
                                self.company_id.currency_id,
                                self.company_id,
                                self.date,
                        )
                        liquidity_balance = self.currency_id._convert(
                                liquidity_amount_currency,
                                self.company_id.currency_id,
                                self.company_id,
                                self.date,
                        )

                        # new
                        liquidity_account = False
                        if self.payment_type in ('outbound', 'transfer'):
                                if self.payment_method_code == 'issue_check':
                                        liquidity_account = self.journal_id.deferred_check_account_id.id
                                else:
                                        liquidity_account = self.outstanding_account_id.id
                        else:
                                if self.payment_method_code == 'received_third_check':
                                        liquidity_account = self.journal_id.holding_check_account_id.id
                                else:
                                        liquidity_account = self.journal_id.payment_credit_account_id.id
                        
                        # new
                        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
                        counterpart_balance = -liquidity_balance - write_off_balance
                        currency_id = self.currency_id.id

                        if self.is_internal_transfer:
                                if self.payment_type == 'inbound':
                                        liquidity_line_name = _('Transfer to %s', self.journal_id.name)
                                else: # payment.payment_type == 'outbound':
                                        liquidity_line_name = _('Transfer from %s', self.journal_id.name)
                        else:
                                liquidity_line_name = self.payment_reference

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

                        line_vals_list = [
                                # Liquidity line.
                                {
                                        'name': liquidity_line_name,
                                        'date_maturity': self.date,
                                        'amount_currency': liquidity_amount_currency,
                                        'currency_id': currency_id,
                                        'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                                        'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': liquidity_account,
                                },
                                # Receivable / Payable.
                                {
                                        'name': self.payment_reference,
                                        'date_maturity': self.date,
                                        'amount_currency': counterpart_amount_currency,
                                        'currency_id': currency_id,
                                        'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                                        'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': self.destination_account_id.id,
                                },
                        ]
                        if not self.currency_id.is_zero(write_off_amount_currency):
                                # Write-off line.
                                line_vals_list.append({
                                        'name': write_off_line_vals.get('name'),
                                        'amount_currency': write_off_amount_currency,
                                        'currency_id': currency_id,
                                        'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                                        'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': write_off_line_vals.get('account_id'),
                                })                        
                        return line_vals_list

        def _synchronize_from_moves(self, changed_fields):
                ''' Update the account.payment regarding its related account.move.
                Also, check both models are still consistent.
                :param changed_fields: A set containing all modified fields on account.move.
                '''
                if self._context.get('skip_account_move_synchronization'):
                        return

                for pay in self.with_context(skip_account_move_synchronization=True):
                        # check of move check module
                        if pay.payment_method_code not in  ('received_third_check','issue_check','delivered_third_check'):
                                # After the migration to 14.0, the journal entry could be shared between the account.payment and the
                                # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
                                if pay.move_id.statement_line_id:
                                        continue

                                move = pay.move_id
                                move_vals_to_write = {}
                                payment_vals_to_write = {}
                                if 'journal_id' in changed_fields:

                                        pay.with_context(skip_account_move_synchronization=False)
                                        pay._synchronize_to_moves({'journal_id'})

                                        if pay.journal_id.type not in ('bank', 'cash'):
                                                raise UserError(_("A payment must always belongs to a bank or cash journal."))

                                if 'line_ids' in changed_fields:
                                        all_lines = move.line_ids
                                        liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                                        
                                        if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                                                raise UserError(_(
                                                        "The journal entry %s reached an invalid state relative to its payment.\n"
                                                        "To be consistent, the journal items must share the same currency."
                                        ) % move.display_name)

                                        if counterpart_lines.account_id.user_type_id.type == 'receivable':
                                                partner_type = 'customer'
                                        else:
                                                partner_type = 'supplier'

                                        liquidity_amount = liquidity_lines.amount_currency

                                        move_vals_to_write.update({
                                                'currency_id': liquidity_lines.currency_id.id,
                                                'partner_id': liquidity_lines.partner_id.id,
                                        })
                                        payment_vals_to_write.update({
                                                'amount': abs(liquidity_amount),
                                                'partner_type': partner_type,
                                                'currency_id': liquidity_lines.currency_id.id,
                                                'destination_account_id': counterpart_lines.account_id.id if counterpart_lines else (writeoff_lines.account_id.id if len(writeoff_lines)==1 else False),
                                                'partner_id': liquidity_lines.partner_id.id,
                                        })
                                        if liquidity_amount > 0.0:
                                                payment_vals_to_write.update({'payment_type': 'inbound'})
                                        elif liquidity_amount < 0.0:
                                                payment_vals_to_write.update({'payment_type': 'outbound'})

                                move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
                                pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

                        else:
                                # After the migration to 14.0, the journal entry could be shared between the account.payment and the
                                # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
                                if pay.move_id.statement_line_id:
                                        continue

                                move = pay.move_id
                                move_vals_to_write = {}
                                payment_vals_to_write = {}

                                if 'journal_id' in changed_fields:
                                        if pay.journal_id.type not in ('bank', 'cash'):
                                                raise UserError(_("A payment must always belongs to a bank or cash journal."))

                                if 'line_ids' in changed_fields:
                                        all_lines = move.line_ids
                                        liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                                        if writeoff_lines and len(writeoff_lines.account_id) != 1:
                                                raise UserError(_(
                                                        "The journal entry %s reached an invalid state relative to its payment.\n"
                                                        "To be consistent, all the write-off journal items must share the same account."
                                                ) % move.display_name)

                                        if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                                                raise UserError(_(
                                                        "The journal entry %s reached an invalid state relative to its payment.\n"
                                                        "To be consistent, the journal items must share the same currency."
                                                ) % move.display_name)

                                        if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                                                raise UserError(_(
                                                        "The journal entry %s reached an invalid state relative to its payment.\n"
                                                        "To be consistent, the journal items must share the same partner."
                                                ) % move.display_name)

                                        if counterpart_lines.account_id.user_type_id.type == 'receivable':
                                                partner_type = 'customer'
                                        else:
                                                partner_type = 'supplier'

                                        liquidity_amount = liquidity_lines.amount_currency

                                        move_vals_to_write.update({
                                                'currency_id': liquidity_lines.currency_id.id,
                                                'partner_id': liquidity_lines.partner_id.id,
                                        })
                                        payment_vals_to_write.update({
                                                'amount': abs(liquidity_amount),
                                                'partner_type': partner_type,
                                                'currency_id': liquidity_lines.currency_id.id,
                                                'destination_account_id': counterpart_lines.account_id.id,
                                                'partner_id': liquidity_lines.partner_id.id,
                                        })
                                        if liquidity_amount > 0.0:
                                                payment_vals_to_write.update({'payment_type': 'inbound'})
                                        elif liquidity_amount < 0.0:
                                                payment_vals_to_write.update({'payment_type': 'outbound'})

                                move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
                                pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

        def _synchronize_to_moves(self, changed_fields):
            ''' Update the account.move regarding the modified account.payment.
            :param changed_fields: A list containing all modified fields on account.payment.
            '''
            if self._context.get('skip_account_move_synchronization'):
                return

            if not any(field_name in changed_fields for field_name in (
                'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
                'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id',
                'post_type','journal_id'
            )):
                return

            for pay in self.with_context(skip_account_move_synchronization=True):
                #     to check if in check model
                if pay.payment_method_code not in  ('received_third_check','issue_check','delivered_third_check'):
                        liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                        # Make sure to preserve the write-off amount.
                        # This allows to create a new payment with custom 'line_ids'.

                        if writeoff_lines:
                                counterpart_amount = sum(counterpart_lines.mapped('amount_currency'))
                                writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
                                # To be consistent with the payment_difference made in account.payment.register,
                                # 'writeoff_amount' needs to be signed regarding the 'amount' field before the write.
                                # Since the write is already done at this point, we need to base the computation on accounting values.
                                if (counterpart_amount > 0.0) == (writeoff_amount > 0.0):
                                        sign = -1
                                else:
                                        sign = 1
                                writeoff_amount = abs(writeoff_amount) * sign

                                write_off_line_vals = {
                                        'name': writeoff_lines[0].name,
                                        'amount': writeoff_amount,
                                        'account_id': writeoff_lines[0].account_id.id,
                                }
                        
                        else:
                                write_off_line_vals = {}

                        line_ids_commands = []
                        line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=False)
                                                
                        if len(line_vals_list) <= 2:
                                if 'journal_id' in changed_fields and len(writeoff_lines) > 1 and len(counterpart_lines)==0 and len(liquidity_lines)==0:
                                        for add in line_vals_list:
                                                line_ids_commands.append((0, 0,add))
                                if counterpart_lines and liquidity_lines:
                                        line_ids_commands = [
                                        (1, liquidity_lines.id, line_vals_list[:1]),
                                        (1, counterpart_lines.id, line_vals_list[1:2]),
                                        ]
                                elif liquidity_lines:
                                        line_ids_commands = [
                                        (1, liquidity_lines.id, line_vals_list[0]),
                                        (0, 0, line_vals_list[1:2])
                                        ]
                                elif counterpart_lines:
                                        line_ids_commands = [
                                        (0, 0, line_vals_list[:1]),
                                        (1, counterpart_lines.id, line_vals_list[1])
                                        ]
                                else:
                                        line_ids_commands = [
                                        (0, 0, line_vals_list[:1]),
                                        (0, 0, line_vals_list[1:2])
                                        ]
                        else:
                                if liquidity_lines:
                                        line_ids_commands = [
                                                (1, liquidity_lines.id, line_vals_list[:1]),
                                        ]
                                else:
                                        line_ids_commands = [
                                                (0, 0, line_vals_list[:1]),
                                        ]
                        for line in writeoff_lines:
                                line_ids_commands.append((2, line.id))
                        if len(line_vals_list) < 3:
                                pass
                        else:
                                for i in range(1,len(line_vals_list)):
                                        line_ids_commands.append((0, 0, line_vals_list[i]))

                        # Update the existing journal items.
                        # If dealing with multiple write-off lines, they are dropped and a new one is generated.                        
                        pay.move_id.write({
                                'partner_id': pay.partner_id.id,
                                'currency_id': pay.currency_id.id,
                                'partner_bank_id': pay.partner_bank_id.id,
                                'line_ids': line_ids_commands,
                        })

                else:
                        liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                        # Make sure to preserve the write-off amount.
                        # This allows to create a new payment with custom 'line_ids'.
                        if writeoff_lines:
                                counterpart_amount = sum(counterpart_lines.mapped('amount_currency'))
                                writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))

                                # To be consistent with the payment_difference made in account.payment.register,
                                # 'writeoff_amount' needs to be signed regarding the 'amount' field before the write.
                                # Since the write is already done at this point, we need to base the computation on accounting values.
                                if (counterpart_amount > 0.0) == (writeoff_amount > 0.0):
                                        sign = -1
                                else:
                                        sign = 1
                                writeoff_amount = abs(writeoff_amount) * sign

                                write_off_line_vals = {
                                'name': writeoff_lines[0].name,
                                'amount': writeoff_amount,
                                'account_id': writeoff_lines[0].account_id.id,
                                }
                        else:
                                write_off_line_vals = {}

                        line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

                        line_ids_commands = [
                                (1, liquidity_lines.id, line_vals_list[:1]),
                                (1, counterpart_lines.id, line_vals_list[1:2]),
                        ]

                        for line in writeoff_lines:
                                line_ids_commands.append((2, line.id))

                        if writeoff_lines:
                                line_ids_commands.append((0, 0, line_vals_list[1:2]))

                        # Update the existing journal items.
                        # If dealing with multiple write-off lines, they are dropped and a new one is generated.
                        pay.move_id.write({
                                'partner_id': pay.partner_id.id,
                                'currency_id': pay.currency_id.id,
                                'partner_bank_id': pay.partner_bank_id.id,
                                'line_ids': line_ids_commands,
                        })

        def unlink(self):
                if self.state == 'posted':
                        raise UserError(_("You cannot delete an entry which has been posted once."))
                return super(StockPayment, self).unlink()

        @api.onchange('destination_account_id')
        def get_value_require(self):
                for rec in self:
                        if rec.destination_account_id:
                                rec.partne_required = False

                                if rec.destination_account_id.is_vendor:
                                        rec.partne_required = True
                                if rec.destination_account_id.is_customer:
                                        rec.partne_required = True
                        else:
                                rec.partne_required = False

        partne_required = fields.Boolean(compute="get_value_require")

        @api.onchange('destination_account_id','post_type','partner_id','journal_id')
        def onchange_account_id(self):
                domain = {}
                for rec in self:
                    if rec.destination_account_id:
                        if rec.destination_account_id.is_customer == True:
                                domain ={'domain': {
                                        'partner_id': [('is_customer', '=', True)],
                                        },
                                        'required': {'partner_id': [('is_customer', '=', True)]}}
                        elif rec.destination_account_id.is_vendor == True:
                                domain ={'domain': {
                                        'partner_id': [('is_vendor', '=', True)],
                                        },
                                'required': {'partner_id': [('is_vendor', '=', True)]}}
                        else:
                                domain ={'domain': {
                                        'partner_id': [(1,'=',1)],
                                         }}

                return domain

        def write(self, vals):
            # OVERRIDE
            res = super(StockPayment,self).write(vals)
            for rec in self:

                if rec.payment_type == 'inbound':
                    journal = 'in'
                elif rec.payment_type == 'outbound':
                    journal = 'out'

                if rec.journal_id and journal and rec.journal_id.pay_type != journal and rec.journal_id.pay_type:
                    raise UserError(_("Please Select Journal"))
            return res
                
class WriteoffAccounts(models.Model):
    _name = 'writeoff.accounts'
    _description = 'Writeoff Accounts'

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False, required="1")
    writeoff_partner_id = fields.Many2one('res.partner', string="Partner", copy=False)
    name = fields.Char('Description')
    analytic_account_id = fields.Many2one('account.analytic.account')
#     upgrade16
#     analytic_tag_ids = fields.Many2many('account.analytic.tag')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_id = fields.Many2one('account.payment', string='Payment Record')


    required_analytical = fields.Boolean(related='writeoff_account_id.required_analytical')    
    

    @api.onchange('writeoff_account_id')
    def get_value_require(self):
        for rec in self:
            if rec.writeoff_account_id:
                rec.partne_required = False
                if rec.writeoff_account_id.is_vendor:
                    rec.partne_required = True
                if rec.writeoff_account_id.is_customer:
                    rec.partne_required = True
            else:
                rec.partne_required = False
                # rec.analytic_req = False
    partne_required = fields.Boolean(compute="get_value_require")

    @api.onchange('writeoff_account_id')
    def onchange_account_id(self):
        domain = {}
        for rec in self:
            if rec.writeoff_account_id.is_customer == True:
                domain ={
                       'domain': {'writeoff_partner_id': [('is_customer', '=', True)]},
                        'required': {'writeoff_partner_id': [('is_customer', '=', True)]}
                }
            elif rec.writeoff_account_id.is_vendor == True:
                domain ={
                        'domain': {'writeoff_partner_id': [('is_vendor', '=', True)]},
                        'required': {'writeoff_partner_id': [('is_vendor', '=', True)]}
                }    
            else:
                domain ={'domain': {'writeoff_partner_id': [(1,'=',1)]}}
            return domain



class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pay_type = fields.Selection([('in','IN'),('out','OUT')])


class AccountAccount(models.Model):

    _inherit = 'account.account'

    is_customer = fields.Boolean('Customer')
    is_vendor = fields.Boolean('Vendor')
