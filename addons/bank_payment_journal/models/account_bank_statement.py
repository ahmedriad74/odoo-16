from odoo import api, fields, models, _
from odoo.tools import pycompat

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    bank_charges = fields.Monetary(compute='get_bank_charges',default=0.0,string='Bank Charges',currency_field='company_currency_id',store=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True, help='Utility field to express amount currency', store=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True, readonly=True)

    @api.depends('amount','journal_id')
    def get_bank_charges(self):
        for payment in self:
            payment.bank_charges = 0.0
            
            if payment.journal_id.type == "bank" and payment.journal_id.bank_charges_account_id and payment.journal_id.charge_percentage > 0:
                payment.bank_charges = payment.amount * (payment.journal_id.charge_percentage/100)

    def create_bank_charges_move_line(self,move):
        debit_account_id = self.journal_id.bank_charges_account_id
        move_id = False
        if isinstance(move, self.env['account.move'].__class__):
            move_id = move.id
        if debit_account_id:
            return {
                'account_id':debit_account_id.id,
                'name': self.name,
                'move_id': move_id,
                'partner_id': self.partner_id and self.partner_id.id or False,
                'debit':self.bank_charges,
                'credit':0.0,
                'statement_line_id': self.id,
                }
    
    def fast_counterpart_creation(self):
        """This function is called when confirming a bank statement and will allow to automatically process lines without
        going in the bank reconciliation widget. By setting an account_id on bank statement lines, it will create a journal
        entry using that account to counterpart the bank account
        """
        payment_list = []
        move_list = []
        account_type_receivable = self.env.ref('account.data_account_type_receivable')
        already_done_stmt_line_ids = [a['statement_line_id'][0] for a in self.env['account.move.line'].read_group([('statement_line_id', 'in', self.ids)], ['statement_line_id'], ['statement_line_id'])]
        managed_st_line = []
        for st_line in self:
            # Technical functionality to automatically reconcile by creating a new move line
            if st_line.account_id and not st_line.id in already_done_stmt_line_ids:
                managed_st_line.append(st_line.id)
                # Create payment vals
                total = st_line.amount
                payment_methods = (total > 0) and st_line.journal_id.inbound_payment_method_ids or st_line.journal_id.outbound_payment_method_ids
                currency = st_line.journal_id.currency_id or st_line.company_id.currency_id
                partner_type = 'customer' if st_line.account_id.user_type_id == account_type_receivable else 'supplier'
                payment_list.append({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total > 0 and 'inbound' or 'outbound',
                    'partner_id': st_line.partner_id.id,
                    'partner_type': partner_type,
                    'journal_id': st_line.statement_id.journal_id.id,
                    'payment_date': st_line.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': st_line._get_communication(payment_methods[0] if payment_methods else False),
                    'name': st_line.statement_id.name or _("Bank Statement %s") % st_line.date,
                })

                # Create move and move line vals
                move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
                aml_dict = {
                    'name': st_line.name,
                    'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                    'credit': st_line.amount > 0 and st_line.amount or 0.0,
                    'account_id': st_line.account_id.id,
                    'partner_id': st_line.partner_id.id,
                    'statement_line_id': st_line.id,
                }
                st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
                move_vals['line_ids'] = [(0, 0, aml_dict)]
                balance_line = self._prepare_reconciliation_move_line(
                    move_vals, -aml_dict['debit'] if st_line.amount < 0 else aml_dict['credit'])

                #create bank charges line
                if st_line.journal_id.type == "bank" and st_line.journal_id.bank_charges_account_id and st_line.bank_charges > 0 and balance_line['debit'] > 0:
                    bank_charges_dict = st_line.create_bank_charges_move_line(move_vals)
                    bank_charges_dict['amount_currency'] = balance_line['amount_currency']
                    bank_charges_dict['currency_id'] = balance_line['currency_id']
                    move_vals['line_ids'].append((0, 0, bank_charges_dict))
                    balance_line['debit'] = balance_line['debit']- st_line.bank_charges

                move_vals['line_ids'].append((0, 0, balance_line))
                move_list.append(move_vals)

        # Creates
        payment_ids = self.env['account.payment'].create(payment_list)
        for payment_id, move_vals in pycompat.izip(payment_ids, move_list):
            for line in move_vals['line_ids']:
                line[2]['payment_id'] = payment_id.id
        move_ids = self.env['account.move'].create(move_list)
        move_ids.post()

        for move, st_line, payment in pycompat.izip(move_ids, self.browse(managed_st_line), payment_ids):
            st_line.write({'move_name': move.name})
            payment.write({'payment_reference': move.name})
