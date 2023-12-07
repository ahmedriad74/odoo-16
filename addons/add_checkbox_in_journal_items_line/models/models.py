# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    receiving_letter = fields.Boolean(string="Receiving Letter")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    receiving_letter = fields.Boolean(string="Receiving Letter")
    receiving_letter_update_date = fields.Datetime(string="Last Update Date")

    def write(self, values):
        for rec in self:
            if 'receiving_letter' in values:
                rec.receiving_letter_update_date = fields.Datetime.now()

        res = super(AccountMoveLine, self).write(values)
        
        return res
        
