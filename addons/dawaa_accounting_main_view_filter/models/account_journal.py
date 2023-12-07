# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    crm_team_name = fields.Char(
        related='crm_team_id.name'
    )
