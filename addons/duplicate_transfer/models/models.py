# -*- coding: utf-8 -*-

from odoo import models, api, _, fields, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    is_duplicated = fields.Boolean(string='Is Duplicated', default=False)
    
    # upgrade16 ==> 'move_lines' become 'move_ids'
    @api.model_create_multi
    def create(self, values):
        result = super().create(values)
        
        (result.move_ids | result.move_ids_without_package).write({
            "picking_type_id": result.picking_type_id,
            'location_id': result.location_id,
            'location_dest_id': result.location_dest_id
        })

        return result

    def action_duplicate(self):
        self.is_duplicated = True
        move_picking_ids = []
        res = self.move_ids
        
        for rec in res:
            move_id = self.env['stock.move'].with_user(SUPERUSER_ID).create({
                'name': rec.name,
                'product_id': rec.product_id.id,
                'description_picking': rec.description_picking,
                'product_uom': rec.product_uom.id,
                'product_uom_qty': rec.product_uom_qty,
                'location_id': rec.location_id.id,
                'location_dest_id': rec.location_dest_id.id,
                'picking_type_id': rec.picking_type_id.id,
                'origin': False,
                'partner_id': False
            })
            move_picking_ids.append(move_id.id)

        ctx = {
            'default_move_ids_without_package': move_picking_ids
        }

        return {
            'name': _('Create Stock/Picking'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_id': self.env.ref('stock.view_picking_form').id,
            'context': ctx
        }
