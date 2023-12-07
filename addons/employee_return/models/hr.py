# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    can_return_after = fields.Boolean('Can Return After 14 Days')

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    can_return_after = fields.Boolean('Can Return After 14 Days')
