# -*- coding: utf-8 -*-

from odoo import models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ReportAuthentication(models.TransientModel):
    _name = 'auth.wizard'
    _description = 'Auth Wizard'

    password = fields.Char(string='Code')

    def action_check_password(self):
        entered_password = self.password
        employee = self.env['hr.employee'].with_user(SUPERUSER_ID).search(
            ['&', ('barcode', '=', entered_password), ('sale_report_access', '=', True)], limit=1)

        if employee and employee.crm_team_id:
            return {
                'name': _('Sales Analysis'),
                'type': 'ir.actions.act_window',
                'view_mode': 'graph,pivot',
                'res_model': 'sale.report',
                'search_view_id': [self.env.ref('sale.view_order_product_search').id, 'search'],
                'views': [
                    [self.env.ref('sale.view_order_product_graph').id, 'graph'], 
                    [self.env.ref('sale_enterprise.sale_report_view_pivot').id, 'pivot']
                ],
                'context': {'search_default_Sales':1, 'group_by_no_leaf':1,'group_by':[]},
                'domain': [('team_id', '=', employee.crm_team_id.id)],
            }
        else:
            raise ValidationError(_("Auth Error: Error code or you haven't a right access"))
