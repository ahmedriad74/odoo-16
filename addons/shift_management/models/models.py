# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShiftManagement(models.Model):
    _name = 'shift.management'
    _description = 'Shift Management'

    name = fields.Char('Shift Name', required=1)
    shift_start_date = fields.Float('Start Date')
    shift_end_date = fields.Float('End Date', digits=(16, 2))
    shift_hours = fields.Integer('Shift Hours')
    shift_type = fields.Selection([('morn', 'Morning'),
                                   ('even', 'Evening'),
                                   ('mid', 'Mid'),
                                   ('night', 'Night')], string='Type', default='morn')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    shift_id = fields.Many2one('shift.management', string='Shift')

class  HrEmployeeBAse(models.AbstractModel):
    _inherit = 'hr.employee.base'

    shift_id = fields.Many2one('shift.management', string='Shift')
