# -*- coding: utf-8 -*-

from odoo import models, fields, _

class SaleReport(models.Model):
    _inherit = "sale.report"

    sale_employee_id = fields.Many2one('hr.employee', string='Sale Employee', readonly=True)
    delivery_employee_id = fields.Many2one('hr.employee', string='Delivery Employee', readonly=True)
    delivery_duration = fields.Char(string='Delivery Duration', readonly=True)

    # upgrade16
    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     fields['sale_employee_id'] = ", s.sale_employee_id as sale_employee_id"
    #     fields['delivery_employee_id'] = ", s.delivery_employee_id as delivery_employee_id"
    #     fields['delivery_duration'] = ", s.delivery_duration as delivery_duration"
    #     groupby += ', s.sale_employee_id, s.delivery_employee_id, s.delivery_duration'
    #     return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['sale_employee_id'] = "s.sale_employee_id"
        res['delivery_employee_id'] = "s.delivery_employee_id"
        res['delivery_duration'] = "s.delivery_duration"
        return res