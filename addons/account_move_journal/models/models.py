# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    ro_invoice_time = fields.Datetime('Date & Time')
    # upgrade16
    # journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
    #                             states={'draft': [('readonly', False)]}, domain="[]",
    #                             check_company=True, default=lambda self: self._search_default_journal())
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        compute='_compute_journal_id', store=True, readonly=False, precompute=True,
        required=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[]",
    )

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        now = datetime.now()
        res['ro_invoice_time'] = now.strftime("%Y-%m-%d %H:%M:%S")
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        now = datetime.now()
        self.ro_invoice_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return res