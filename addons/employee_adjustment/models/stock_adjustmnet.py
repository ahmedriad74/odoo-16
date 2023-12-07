# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError

# HOLD
# class StockInventory(models.Model):
#     _inherit = "stock.inventory"

#     adj_employee_id = fields.Many2one(
#         string='Adjustment Employee',
#         comodel_name='hr.employee',
#         readonly=True
#     )

#     barcode = fields.Char(string="Code", required=True)

#     @api.onchange('barcode')
#     def _onchange_adj_barcode(self):
#         if self.barcode:
#             employee = self.env['hr.employee'].search([('barcode', '=', self.barcode), ('is_adjustment', '=', True)])

#             if not employee:
#                 raise ValidationError(_('Wrong Code.'))
#             else:
#                 self.adj_employee_id = employee
