# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    delivery_employee_id = fields.Many2one(
        string='Delivery Employee',
        comodel_name='hr.employee',
        compute='_compute_delivery_employee_id',
        store=True,  
    )
    order_wd = fields.Selection(
        string='Order WD',
        selection=[('not_wd', 'Not-WD'), ('walk_in', 'Walk-in'), ('delivery', 'Delivery')],
        default='not_wd'
    )
    sale_employee_id = fields.Many2one(
        string='Sale Employee',
        comodel_name='hr.employee',
        readonly=True,
        copy=False
    )

    @api.depends('order_id.picking_ids')
    def _compute_delivery_employee_id(self):
        for move in self:
            move.delivery_employee_id = move.order_id.picking_ids.delivery_employee_id

    def copy(self, default=None):
        if self.env.user.has_group('account.group_account_manager'):
            return super().copy(default=default)
        else:
            raise UserError(_('Can\'t be duplicated'))