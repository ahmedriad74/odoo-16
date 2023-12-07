# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
class stockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super(stockReturnPicking,self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        if res['quantity'] <= 0:
            res['negative_flag'] = True
        else:
            res['negative_flag'] = False
        return res

    def check_chroninc_returns(self, order, return_picking):
        if order.pricelist_id.free_products_by_margin:
            for mv in return_picking.move_line_ids_without_package:
                if mv.product_id.levelf_id.name == 'chronic' and\
                   mv.move_id.sale_line_id.product_qty_before_free_one < 0:
                    raise ValidationError("This order has offfer and can't be returned")
                mv.move_id.sale_line_id.customer_consumption_id.remaining_prod_qty += mv.product_uom_qty
                mv.move_id.sale_line_id.customer_consumption_id.restart = False

    def _create_returns(self):
        new_picking_id, pick_type_id = super()._create_returns()

        return_picking = self.env['stock.picking'].browse(new_picking_id)
        order = self.env['sale.order'].search([('name', '=',self.picking_id.origin)])
        warehouse = order.warehouse_id

        self.check_chroninc_returns(order, return_picking)

        if warehouse.is_return_set_to_done and return_picking: 
            return_picking.action_assign()

            if return_picking.move_line_ids_without_package:
                for mv in return_picking.move_line_ids_without_package:
                    mv.lot_id = mv.move_id.sale_line_id.py_lot_id

                return_picking.action_confirm()
                return_picking.action_assign()

            if return_picking.move_line_ids_without_package:
                for mv in return_picking.move_line_ids_without_package:
                    mv.qty_done = mv.product_uom_qty
            else:
                for mv in return_picking.move_ids_without_package:
                    mv.quantity_done = mv.product_uom_qty
                                            
            return_picking.with_context(skip_expired=True).button_validate()

        if warehouse.create_cn:
            order._create_invoices(final=True)  

        invoice_ids = order.invoice_ids.filtered(lambda move: move.state == 'draft')
        
        if warehouse.validate_cn and invoice_ids:
            for invoice in invoice_ids:
                invoice.action_post()

        return new_picking_id, pick_type_id
         
class stockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    negative_flag = fields.Boolean()
