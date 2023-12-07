# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):

    _inherit = "account.payment"

    casher_employee_id = fields.Many2one(
        string='Casher Employee',
        comodel_name='hr.employee',
        readonly=True
    )

    py_visa_receipt_number = fields.Char(
        string="Receipt Number", readonly=True)

    show_visa_receipt_number = fields.Boolean(
        compute='_compute_show_visa_receipt_number')

    @api.depends('journal_id')
    def _compute_show_visa_receipt_number(self):
        for wizard in self:
            wizard.show_visa_receipt_number = True if wizard.journal_id.type == 'bank' else False

    @api.model_create_multi
    def create(self, values):
        result = super(AccountPayment, self).create(values)
        
        if not self.env.user.has_group('account.group_account_manager') and result.journal_id.crm_team_id and self.env.user \
            not in result.journal_id.crm_team_id.member_ids:
            raise ValidationError(
                _('You are not allowed to create payment in this journal.'))

        return result
