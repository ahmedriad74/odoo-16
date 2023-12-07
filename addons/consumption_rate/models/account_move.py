# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    move_type = fields.Selection(related='move_id.move_type', store=True, readonly=True)
    location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.location',
        ondelete='restrict',
        compute='_compute_location_id',
        store=True
    )
    
    @api.depends('move_id.team_id')
    def _compute_location_id(self):
        for record in self:
            warehouse_id = self.env['stock.warehouse'].search([('crm_team_id','=',record.move_id.team_id.id)])

            if warehouse_id:
                record.location_id = warehouse_id.lot_stock_id.id
            else:
                record.location_id = False
                