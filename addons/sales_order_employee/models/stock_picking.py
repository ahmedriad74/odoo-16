# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    area = fields.Selection(
        string='Area',
        selection=[('alex', 'Alexandria'), ('tanta', 'Tanta')],
        compute='_compute_area')
    delivery_employee_id = fields.Many2one(
        string='Delivery Employee',
        comodel_name='hr.employee',
        domain="[('delivery_area','=',area)]",
        copy=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        readonly=True
    )
    delivery_barcode = fields.Char(string="Delivery Code", copy=False)
    order_wd = fields.Selection(
        string='Order WD',
        selection=[('not_wd', 'Not-WD'), ('walk_in', 'Walk-in'),
                   ('delivery', 'Delivery')],
        copy=False,
        compute='_compute_order_wd', store=True
    )
    processing_employee = fields.Many2one('hr.employee', copy=False)
    # used for domain view
    warehouse_team_id = fields.Many2one(
        'crm.team', 'Warehouse User', compute='_compute_warehouse_team_id', store=True)

    @api.depends('picking_type_id')
    def _compute_area(self):
        for record in self:
            record.area = record.picking_type_id.warehouse_id.crm_team_id.area

    @api.onchange('delivery_barcode', 'area')
    def _onchange_delivery_barcode(self):
        if self.delivery_barcode and self.area:
            employee = self.env['hr.employee'].search([('barcode', '=', self.delivery_barcode),
                                                       ('delivery_area', '=', self.area)])

            if not employee:
                raise ValidationError(_('Wrong Code.'))
            else:
                self.delivery_employee_id = employee

    @api.depends('sale_id')
    def _compute_order_wd(self):
        for picking in self:
            if not picking.sale_id:
                picking.order_wd = 'not_wd'
            else:
                if picking.picking_type_code == 'outgoing':
                    picking.order_wd = 'walk_in' if not \
                        any(line.is_delivery for line in picking.sale_id.order_line) else 'delivery'
                else:
                    picking.order_wd = 'walk_in'

    @api.depends('picking_type_id')
    def _compute_warehouse_team_id(self):
        for picking in self:
            picking.warehouse_team_id = False
            warehouse = picking.picking_type_id.warehouse_id

            if warehouse:
                picking.warehouse_team_id = warehouse.crm_team_id

    def py_assign_delivery(self):
        return {
            'name': _('Assign Delivery'),
            'type': 'ir.actions.act_window',
            'res_model': 'assign.delivery',
            'target': 'new',
            'context': self.env.context,
            'view_mode': 'form'
        }
