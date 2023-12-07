# -*- coding: utf-8 -*-

from odoo import models, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, values):
        result = super().create(values)

        if result.picking_id:
            result.write({
                'location_id': result.picking_id.location_id.id,
                'location_dest_id': result.picking_id.location_dest_id.id,
                'picking_type_id': result.picking_id.picking_type_id.id
            })

        return result

    