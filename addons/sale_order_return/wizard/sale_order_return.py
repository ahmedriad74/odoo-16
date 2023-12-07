# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderReturn(models.TransientModel):
    _name = 'sale.order.return'
    _description = 'Sale Order Return'

    order = fields.Char('Order')

    def search_order(self):
        order = self.env['sale.order'].search([('name','=',self.order)])

        if not order:
            raise UserError(_('No Order Found'))

        picking_order = self.env['stock.picking'].search([
            ('origin', '=', order.name),
            ('warehouse_team_id','=',order.team_id.id),
            ('state','=','done')
        ])

        if picking_order:
            ctx = ({
                'default_partner_id': picking_order.partner_id.id,
                'search_default_picking_type_id': picking_order.picking_type_id
            })

            return {
                'name': _('Return Picking'),
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'res_id': picking_order.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
            }
        else:
            raise UserError(_('No Order Found To Return.'))
        
        
        
