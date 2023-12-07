# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountPaymentRegister(models.TransientModel):

    _inherit = "account.payment.register"

    barcode = fields.Char(string="Code", required=True)

    py_visa_receipt_number = fields.Char(string="Receipt Number") 

    show_visa_receipt_number = fields.Boolean(
        compute='_compute_show_visa_receipt_number')

    @api.depends('journal_id')
    def _compute_show_visa_receipt_number(self):
        for wizard in self:
            wizard.show_visa_receipt_number = True if wizard.journal_id.type == 'bank' else False


    def _create_payments(self):
        
        if not self.env.user.has_group('account.group_account_manager'):
            employee = self.env['hr.employee'].search([('barcode', '=', self.barcode), ('is_casher', '=', True), \
                ('crm_team_id', '=', self.team_id.id)])
        else:
            employee = self.env['hr.employee'].search([('barcode', '=', self.barcode), ('is_casher', '=', True)])
            
        if not employee:
            raise ValidationError(_('Wrong Code.'))
            
        payment = super()._create_payments()

        payment['casher_employee_id'] = employee.id
        payment['py_visa_receipt_number'] = self.py_visa_receipt_number

        if len(self.line_ids) > 0:
            sale_order = self.env['sale.order'].search([('invoice_ids', '=', self.line_ids[0].move_id.id)])        
            
            if sale_order and self.line_ids[0].move_id.move_type == 'out_invoice' \
                and sale_order.order_wd == 'delivery'\
                    and sale_order.delivery_employee_id:
                sale_order.write({'delivery_date_in':datetime.now()})

        return payment