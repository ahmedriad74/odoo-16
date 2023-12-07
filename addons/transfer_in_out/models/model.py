# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit="stock.picking"

    is_transfer_in = fields.Boolean()
    is_transfer_out = fields.Boolean()
    transfer_in_type = fields.Selection([('cosmo', 'Cosmo'), ('med', 'Medical')], string='Type')

    @api.onchange('is_transfer_in','is_transfer_out')
    def add_default_operation_type(self):
        for rec in self:
            crm = self.env['crm.team'].search([('member_ids','=',self.env.user.id)])

            if len(crm):
                warehouse_id = self.env['stock.warehouse'].search([('crm_team_id','=',crm[0].id)])

                if len(warehouse_id):    
                    if rec.is_transfer_in:
                        rec.picking_type_id = self.env['stock.picking.type'].search([('code','=','internal'),('warehouse_id','=', warehouse_id[0].id), ('default_location_dest_id', '=', warehouse_id[0].lot_stock_id.id)]) 
                        rec.location_dest_id = rec.picking_type_id.default_location_dest_id.id
                    if rec.is_transfer_out:
                        rec.picking_type_id = self.env['stock.picking.type'].search([('code','=','internal'),('warehouse_id','=', warehouse_id[0].id), ('default_location_src_id', '=', warehouse_id[0].lot_stock_id.id)])        
                        rec.location_id = rec.picking_type_id.default_location_src_id.id
    
    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_code != 'internal' and not (self.is_transfer_in or self.is_transfer_out):
            super(StockPicking, self).onchange_picking_type()
        elif (self.is_transfer_in or self.is_transfer_out):
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            if not self.is_transfer_out:
                self.location_id = location_id

    @api.onchange('location_dest_id')
    def get_operation_type(self):
        for rec in self:
            if rec.picking_type_code == 'internal' or not rec.picking_type_code:
                picking_types = self.env['stock.picking.type'].search([('code','=','internal'), ('default_location_dest_id','=',rec.location_dest_id.id)])
                rec.picking_type_id = picking_types if len(picking_types) else False

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        products = set()

        if res.is_transfer_in:
            for line in res.move_ids_without_package:
                if res.transfer_in_type == 'med'\
                    and line.product_id.levela_id\
                    and ('دواء') not in line.product_id.levela_id.name:
                        products.add(line.product_id.name)
        
        if products:
            raise ValidationError(f"These products [{','.join(products)}] are not medical")
        return res
