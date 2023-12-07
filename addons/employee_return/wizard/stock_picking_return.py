# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    team_id = fields.Many2one('crm.team', 'Sales Team', related='picking_id.picking_type_id.warehouse_id.crm_team_id')
    barcode = fields.Char(string="Code", required=True)

    def _create_returns(self):
        employee = self.env['hr.employee'].search([('barcode', '=', self.barcode), ('return_access', '=', True), \
            ('crm_team_id', '=', self.team_id.id)])

        if not employee:
            raise ValidationError(_('Wrong Code.'))
        
        date = fields.Datetime.today() - self.picking_id.date_done
        
        if date.days >= 14 and self.picking_id.picking_type_code == 'outgoing' and not employee.can_return_after:
            raise UserError(_("Can't return order after 14 days."))
            
        new_picking_id, picking_type_id = super()._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        new_picking.write({
            'return_sales_employee_id': employee
        })

        return new_picking_id, picking_type_id