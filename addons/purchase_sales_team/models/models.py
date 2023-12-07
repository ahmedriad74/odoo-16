# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_picking_type(self, company_id):
        team_id = self.env['crm.team']._get_default_team_id()
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'),
                                                              ('warehouse_id.company_id',
                                                               '=', company_id),
                                                              ('warehouse_id.crm_team_id', '=', team_id.id)])

        if not picking_type:
            picking_type = super(
                PurchaseOrder, self)._get_picking_type(company_id)

        return picking_type[:1]

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def _prepare_invoice(self):
        result = super(PurchaseOrder, self)._prepare_invoice()

        result['user_id'] = self.user_id.id
        result['invoice_user_id'] = self.user_id.id
        result['team_id'] = self.team_id.id

        return result
