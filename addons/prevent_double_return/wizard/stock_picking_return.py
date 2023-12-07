
from odoo import fields, models, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        result = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)

        if stock_move.picking_id.origin and ("Return of" in stock_move.picking_id.origin or "إعادة" in stock_move.picking_id.origin):
            raise UserError(_('Return Can\'t be created.'))
        
        '''if result['quantity'] == 0:
            raise UserError(_('Return already created.'))'''

        return result
