# -*- coding: utf-8 -*-

from odoo import models, api, _, SUPERUSER_ID
from odoo.addons import stock

# Remove action_assign after backorder creation

def _create_backorder(self):
    """ This method is called when the user chose to create a backorder. It will create a new
    picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
    """
    backorders = self.env['stock.picking']
    for picking in self:
        # upgrade16 ==> 'move_lines' become 'move_ids'
        moves_to_backorder = picking.move_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        if moves_to_backorder:
            backorder_picking = picking.copy({
                'name': '/',
                'move_ids': [],
                'move_line_ids': [],
                'backorder_id': picking.id
            })
            picking.message_post(
                body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                    backorder_picking.id, backorder_picking.name))
            moves_to_backorder.write({'picking_id': backorder_picking.id})
            moves_to_backorder.move_line_ids.package_level_id.write({'picking_id':backorder_picking.id})
            moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
            backorders |= backorder_picking

    #Unreserve qty from backorders     
    if backorders:
        backorders.do_unreserve()

    return backorders

stock.models.stock_picking.Picking._create_backorder = _create_backorder
