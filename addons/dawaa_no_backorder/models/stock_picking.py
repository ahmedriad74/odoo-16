# -*- coding: utf-8 -*-

from odoo import  _
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.addons import stock
from odoo.exceptions import UserError


def button_validate(self):
    # Clean-up the context key at validation to avoid forcing the creation of immediate
    # transfers.
    ctx = dict(self.env.context)
    ctx.pop('default_immediate_transfer', None)
    self = self.with_context(ctx)

    # Sanity checks.
    pickings_without_moves = self.browse()
    pickings_without_quantities = self.browse()
    pickings_without_lots = self.browse()
    products_without_lots = self.env['product.product']
    for picking in self:
        # upgrade16 ==> 'move_lines' become 'move_ids'
        # if not picking.move_lines and not picking.move_line_ids:
        if not picking.move_ids and not picking.move_line_ids:
            pickings_without_moves |= picking

        picking.message_subscribe([self.env.user.partner_id.id])
        picking_type = picking.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        # upgrade16 ==> 'product_qty' become 'reserved_qty'
        # no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
        no_reserved_quantities = all(float_is_zero(move_line.reserved_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            pickings_without_quantities |= picking

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = picking.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        pickings_without_lots |= picking
                        products_without_lots |= product

    if not self._should_show_transfers():
        if pickings_without_moves:
            raise UserError(_('Please add some items to move.'))
        if pickings_without_quantities:
            raise UserError(self._get_without_quantities_error_message())
        if pickings_without_lots:
            raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
    else:
        message = ""
        if pickings_without_moves:
            message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
        if pickings_without_quantities:
            message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
        if pickings_without_lots:
            message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
        if message:
            raise UserError(message.lstrip())

    # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
    # moves and/or the context and never call `_action_done`.
    if not self.env.context.get('button_validate_picking_ids'):
        self = self.with_context(button_validate_picking_ids=self.ids)
    res = self._pre_action_done_hook()
    if res is not True:
        return res

    # Call `_action_done`.
    # override part
    if  self.location_id.py_warehouse_id.is_main_wh and self.env.context.get('picking_ids_not_to_backorder'):
        pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        return True
    # 
    if self.env.context.get('picking_ids_not_to_backorder'):
        pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
        pickings_to_backorder = self - pickings_not_to_backorder
    else:
        pickings_not_to_backorder = self.env['stock.picking']
        pickings_to_backorder = self
    pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
    pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
    return True

def _pre_action_done_hook(self):
    # override part
    if self.location_id.py_warehouse_id.is_main_wh and not self.env.context.get('skip'):
        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            ctx = self._context.copy()
            ctx['skip'] = True
            self.env.context = ctx
            return self.browse(pickings_to_validate)\
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.ids)\
                .button_validate()
        
    # 
    if not self.env.context.get('skip_immediate'):
        pickings_to_immediate = self._check_immediate()
        if pickings_to_immediate:
            return pickings_to_immediate._action_generate_immediate_wizard(show_transfers=self._should_show_transfers())

    if not self.env.context.get('skip_backorder'):
        pickings_to_backorder = self._check_backorder()
        if pickings_to_backorder:
            return pickings_to_backorder._action_generate_backorder_wizard(show_transfers=self._should_show_transfers())
    return True


stock.models.stock_picking.Picking._pre_action_done_hook = _pre_action_done_hook
stock.models.stock_picking.Picking.button_validate = button_validate
