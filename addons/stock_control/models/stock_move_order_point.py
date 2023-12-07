# -*- coding: utf-8 -*-

from odoo import models, fields
# from odoo.addons import stock


class StockMoveOrderPoint(models.Model):
    _name = "stock.move.orderpoint"
    _description = 'Stock Move Order Point'

    move_ids = fields.One2many('stock.move', 'stock_move_orderpoint_id')
    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint')


# StockMove = stock.models.stock_move.StockMove
# def _action_done(self, cancel_backorder=False):
#     self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves
#     moves = self.exists().filtered(lambda x: x.state not in ('done', 'cancel'))
#     moves_todo = self.env['stock.move']

#     # Cancel moves where necessary ; we should do it before creating the extra moves because
#     # this operation could trigger a merge of moves.
#     sml_to_delete = self.env['stock.move.line']
#     for move in moves:
#         # Other Orderpoint Moves
#         if move.picking_id.picking_type_id.code == 'internal':
#             po_move_ids = move.stock_move_orderpoint_id.move_ids.filtered(lambda m: m.id != move.id)

#             if po_move_ids:
#                 for po_move in po_move_ids:
#                     if move.product_uom_qty <= po_move.product_uom_qty:
#                         sml_to_delete += (move.move_line_ids)

#                 if sml_to_delete:
#                     activity_vals = {
#                         'res_id': move.picking_id.id,
#                         'res_model_id': self.env.ref('stock.model_stock_picking').id,
#                         'summary': 'Removed Stock Moves',
#                         'note': sml_to_delete.mapped(lambda line: {
#                             'Name': line.product_id.name,
#                             'QTY': line.product_uom_qty,
#                         }),
#                         'date_deadline': fields.Date.today(),
#                         'user_id':  self.env.user.id
#                     }

#                     self.env['mail.activity'].sudo().with_context(mail_activity_quick_update=True).create(activity_vals)
#                     sml_to_delete.unlink()

#         if move.quantity_done <= 0:
#             if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0 or cancel_backorder:
#                 move._action_cancel()

#     # Create extra moves where necessary
#     for move in moves:
#         if move.state == 'cancel' or move.quantity_done <= 0:
#             continue

#         moves_todo |= move._create_extra_move()

#     moves_todo._check_company()
#     # Split moves where necessary and move quants
#     backorder_moves_vals = []
#     for move in moves_todo:
#         # To know whether we need to create a backorder or not, round to the general product's
#         # decimal precision and not the product's UOM.
#         rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         if float_compare(move.quantity_done, move.product_uom_qty, precision_digits=rounding) < 0:
#             # Need to do some kind of conversion here
#             qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
#             new_move_vals = move._split(qty_split)
#             backorder_moves_vals += new_move_vals
#     backorder_moves = self.env['stock.move'].create(backorder_moves_vals)
#     backorder_moves._action_confirm(merge=False)
#     if cancel_backorder:
#         backorder_moves.with_context(moves_todo=moves_todo)._action_cancel()
#     moves_todo.mapped('move_line_ids').sorted()._action_done()
#     # Check the consistency of the result packages; there should be an unique location across
#     # the contained quants.
#     for result_package in moves_todo\
#             .mapped('move_line_ids.result_package_id')\
#             .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
#         if len(result_package.quant_ids.filtered(lambda q: not float_is_zero(abs(q.quantity) + abs(q.reserved_quantity), precision_rounding=q.product_uom_id.rounding)).mapped('location_id')) > 1:
#             raise UserError(_('You cannot move the same package content more than once in the same transfer or split the same package into two location.'))
#     picking = moves_todo.mapped('picking_id')
#     moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})

#     move_dests_per_company = defaultdict(lambda: self.env['stock.move'])
#     for move_dest in moves_todo.move_dest_ids:
#         move_dests_per_company[move_dest.company_id.id] |= move_dest
#     for company_id, move_dests in move_dests_per_company.items():
#         move_dests.sudo().with_company(company_id)._action_assign()

#     # We don't want to create back order for scrap moves
#     # Replace by a kwarg in master
#     if self.env.context.get('is_scrap'):
#         return moves_todo

#     if picking and not cancel_backorder:
#         picking._create_backorder()
#     return moves_todo


# stock.models.stock_move.StockMove._action_done = _action_done