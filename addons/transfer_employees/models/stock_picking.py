# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sender_employee = fields.Many2one(
        string='Sender Employee',
        comodel_name='hr.employee',
        readonly=True
    )
    receiver_employee = fields.Many2one(
        string='Receiver Employee',
        comodel_name='hr.employee',
        readonly=True
    )
    sender_employee_code = fields.Char(string="Sender Code")
    receiver_employee_code = fields.Char(string="Receiver Code")

    def button_validate(self):
        if self.picking_type_code == 'internal'\
                    and self.state == 'validate2'\
                    and not self.receiver_employee_code:
            raise ValidationError(_('Please provide receiver code.'))
        return super().button_validate()

    @api.onchange('sender_employee_code')
    def _onchange_sender_employee_barcode(self):
        if self.picking_type_code == 'internal' and self.sender_employee_code:
            location_from_team = self.location_id.py_warehouse_id.crm_team_id
            employee = self.env['hr.employee'].search([
                                                    ('barcode', '=', self.sender_employee_code), 
                                                    ('crm_team_id', '=', location_from_team.id)])

            if not employee:
                raise ValidationError(_('Wrong Sender User Code.'))
            else:
                self.sender_employee = employee  

    @api.onchange('receiver_employee_code')
    def _onchange_receiver_employee_code(self):
        if self.picking_type_code == 'internal' and self.receiver_employee_code:
            destination_team = self.location_dest_id.py_warehouse_id.crm_team_id
            employee = self.env['hr.employee'].search([
                                                    ('barcode', '=', self.receiver_employee_code), 
                                                    ('crm_team_id', '=', destination_team.id)])

            if not employee:
                raise ValidationError(_('Wrong Receiver User Code.'))
            else:
                self.receiver_employee = employee  
