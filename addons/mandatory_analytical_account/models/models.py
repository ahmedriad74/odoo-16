# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    required_analytical = fields.Boolean(related='account_id.required_analytical')    
    # upgrade16 ==> 'move_state' is already exist as 'move_type'
    # move_state = fields.Selection(related='move_id.move_type')


class Account(models.Model):
    _inherit = 'account.account'

    required_analytical = fields.Boolean()    
