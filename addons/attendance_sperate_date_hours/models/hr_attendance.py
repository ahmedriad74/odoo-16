# -*- coding: utf-8 -*-

from odoo import models, fields,api, _, exceptions
from odoo.tools import format_datetime
from datetime import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    attendance_date = fields.Date()
    hour_in = fields.Char()
    hour_out = fields.Char()
    update = fields.Boolean(string='Update', default=False)

    def read(self, fields=None, load='_classic_read'):
        res = super(HrAttendance, self).read(fields=fields, load=load)
        for r in self.filtered(lambda x:x.update):
            r.write({'update':False})
            r.get_check_in_out()
        return res

    def get_check_in_out(self):
        for rec in self:
            if rec.attendance_date:
                if len(rec.hour_in):
                    date = str(rec.attendance_date) + " " + rec.hour_in
                    date_time = datetime.strptime(date, '%Y-%m-%d %I:%M:%S %p')
                    rec.check_in = date_time

                if len(rec.hour_out):
                    date_out = str(rec.attendance_date) + " " + rec.hour_out
                    date_time = datetime.strptime(date_out, '%Y-%m-%d %I:%M:%S %p')                    
                    rec.check_out = date_time

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
                })

            if not attendance.check_out and not attendance.hour_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                    })
