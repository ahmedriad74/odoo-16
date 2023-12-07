# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AssignDelivery(models.TransientModel):
    _name = 'assign.delivery'
    _description = 'Assign Delivery'

    delivery_employee_id = fields.Many2one(
        string='Delivery Employee',
        comodel_name='hr.employee',
        copy=False,
        readonly=True
    )
    delivery_barcode = fields.Char(string="Delivery Code", copy=False)

    @api.onchange('delivery_barcode')
    def _onchange_delivery_barcode(self):
        if self.delivery_barcode:
            selected_ids = self.env.context.get('active_ids', [])
            activity_data = self.env['stock.picking'].browse(selected_ids)
            employee = False
            
            if len(activity_data):
                employee = self.env['hr.employee'].search(
                    [('barcode', '=', self.delivery_barcode),('delivery_area', '=', activity_data[0].area)])

            if not employee or len(list(dict.fromkeys(activity_data.mapped('area')))) > 1:
                raise ValidationError(_('Wrong Code.'))
            else:
                self.delivery_employee_id = employee

    def action_assign_delivery(self):
        selected_ids = self.env.context.get('active_ids', [])
        activity_data = self.env['stock.picking'].browse(selected_ids)

        activity_data = activity_data.filtered(lambda picking: (
            picking.picking_type_code == 'internal' or picking.order_wd == 'delivery') and picking.state == 'assigned')

        for picking in activity_data:
            picking.delivery_barcode = self.delivery_barcode
            picking._onchange_delivery_barcode()
