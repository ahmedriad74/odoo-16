# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_adjustment = fields.Boolean('Adjustment')

class  HrEmployeeBAse(models.AbstractModel):
    _inherit = 'hr.employee.base'

    is_adjustment = fields.Boolean('Adjustment')
