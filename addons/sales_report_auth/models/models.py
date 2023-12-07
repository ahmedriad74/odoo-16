# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sale_report_access = fields.Boolean('Sale Report Access', default=False)
    return_access = fields.Boolean(string='Retrun Access')


class HrEmployeeBAse(models.AbstractModel):
    _inherit = 'hr.employee.base'

    sale_report_access = fields.Boolean('Sale Report Access', default=False)
    
    
