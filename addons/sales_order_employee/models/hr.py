# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )
    is_sale = fields.Boolean('Sales')
    delivery_area = fields.Selection(
        string='Delivery Area',
        selection=[('alex', 'Alexandria'), ('tanta', 'Tanta')]
    )
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user", copy=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if not result and name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            args = [('barcode', operator, name)] + args
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

class  HrEmployeeBAse(models.AbstractModel):
    _inherit = 'hr.employee.base'

    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )
    is_sale = fields.Boolean('Sales')
    delivery_area = fields.Selection(
        string='Delivery Area',
        selection=[('alex', 'Alexandria'), ('tanta', 'Tanta')]
    )
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user", copy=False)
    is_casher = fields.Boolean()
    is_purchase = fields.Boolean('Purchase')
