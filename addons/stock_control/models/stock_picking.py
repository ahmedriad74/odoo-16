# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.addons import stock
from collections import defaultdict

class StockPicking(models.Model):
    _inherit = "stock.picking"

    bag = fields.Integer(string='كيسة', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    box = fields.Integer(string='كرتونة', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    fridge = fields.Integer(string='ثلاجة', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    first_move_line = fields.Text('Products', compute='_compute_picking_products', store=True)

    # upgrade16 ==> 'move_lines' become 'move_ids'
    @api.depends('move_ids')
    def _compute_picking_products(self):
        for record in self:
            picking_products = ''

            for move in record.move_ids:
                picking_products += '[' + str(move.product_uom_qty) + ']' + \
                    ' ' + str(move.product_id.name) + '\n'
                break

            record.first_move_line = picking_products

    def action_done_move_line(self):
        for rec in self:
            for line in rec.move_line_ids:
                if rec.picking_type_code == 'internal':
                    line.qty_done = line.product_uom_qty
                    line._onchange_qty_done()

    def action_confirm_move_line(self):
        for rec in self:
            for line in rec.move_line_ids:

                if line.product_uom_qty == line.qty_done:
                    line.confirm_flag = True

    def action_picking_move_line_tree(self):
        return {
            'name': _('Stock Move Lines'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            # 'view_id': self.env.ref('stock.view_stock_move_line_operation_tree').id,
            'view_id': self.env.ref('stock_control.view_picking_move_line_tree').id,
            'res_model': 'stock.move.line',
            'context': {'show_lots_m2o': True, 'show_reserved_quantity': True, 'lock_lot_change': True},
            #'context': {'show_lots_text': False, 'show_reserved_quantity': True},
            'domain': [('picking_id', 'in', self.ids), ('confirm_flag','=',False)],
            'target': 'current',
        }
    
    def button_validate(self):
        pickings = self.filtered(
            lambda p: p.picking_type_code == 'incoming' and p.location_id.location_id != p.location_dest_id.location_id\
            and self.env.user not in p.location_dest_id.py_warehouse_id.crm_team_id.member_ids)

        if not pickings:
            return super(StockPicking, self).button_validate()
        else:
            raise UserError(_("Only destination location employee can validate this."))
        

@api.depends('move_type', 'immediate_transfer', 'move_ids.state', 'move_ids.picking_id')
def _compute_state(self):
    ''' State of a picking depends on the state of its related stock.move
    - Draft: only used for "planned pickings"
    - Waiting: if the picking is not ready to be sent so if
        - (a) no quantity could be reserved at all or if
        - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
    - Waiting another move: if the picking is waiting for another move
    - Ready: if the picking is ready to be sent so if:
        - (a) all quantities are reserved or if
        - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
    - Done: if the picking is done.
    - Cancelled: if the picking is cancelled
    '''
    picking_moves_state_map = defaultdict(dict)
    picking_move_lines = defaultdict(set)
    for move in self.env['stock.move'].search([('picking_id', 'in', self.ids)]):
        picking_id = move.picking_id
        move_state = move.state
        picking_moves_state_map[picking_id.id].update({
            'any_draft': picking_moves_state_map[picking_id.id].get('any_draft', False) or move_state == 'draft',
            'all_cancel': picking_moves_state_map[picking_id.id].get('all_cancel', True) and move_state == 'cancel',
            'all_cancel_done': picking_moves_state_map[picking_id.id].get('all_cancel_done', True) and move_state in ('cancel', 'done'),
            'all_done_are_scrapped': picking_moves_state_map[picking_id.id].get('all_done_are_scrapped', True) and (move.scrapped if move_state == 'done' else True),
            'any_cancel_and_not_scrapped': picking_moves_state_map[picking_id.id].get('any_cancel_and_not_scrapped', False) or (move_state == 'cancel' and not move.scrapped),
        })
        picking_move_lines[picking_id.id].add(move.id)
    for picking in self:
        picking_id = (picking.ids and picking.ids[0]) or picking.id
        if not picking_moves_state_map[picking_id]:
            picking.state = 'draft'
        elif picking_moves_state_map[picking_id]['any_draft']:
            picking.state = 'draft'
        elif picking_moves_state_map[picking_id]['all_cancel']:
            picking.state = 'cancel'
        elif picking_moves_state_map[picking_id]['all_cancel_done']:
            if picking_moves_state_map[picking_id]['all_done_are_scrapped'] and picking_moves_state_map[picking_id]['any_cancel_and_not_scrapped']:
                picking.state = 'cancel'
            else:
                picking.state = 'done'
        # override section
        elif picking.state == 'validate2':
            continue
        # 
        else:
            relevant_move_state = self.env['stock.move'].browse(picking_move_lines[picking_id])._get_relevant_state_among_moves()
            if picking.immediate_transfer and relevant_move_state not in ('draft', 'cancel', 'done'):
                picking.state = 'assigned'
            elif relevant_move_state == 'partially_available':
                picking.state = 'assigned'
            else:
                picking.state = relevant_move_state
    

stock.models.stock_picking.Picking._compute_state = _compute_state