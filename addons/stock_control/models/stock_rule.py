# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import models, api, _, SUPERUSER_ID
from odoo.addons import stock
from odoo.tools import float_compare


class StockRule(models.Model):
    _inherit = "stock.rule"

    # Split stock picking by order point batch
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        move_values = super()._get_stock_move_values(product_id, product_qty,
                                                     product_uom, location_id, name, origin, company_id, values)
       
        if values.get('orderpoint_id') and values.get('py_batch'):
            py_batch = values.get('py_batch')
            procurement_group = self.env["procurement.group"].search([('name', '=', py_batch)])

            if procurement_group:
                move_values['group_id'] = procurement_group
            else:
                move_values['group_id'] = self.env["procurement.group"].create({'name': py_batch})

            move_values['group_id'] = move_values['group_id'].id
            move_values['origin'] = py_batch
            move_values['py_batch_source'] = values.get('py_batch_source')

        elif values.get('orderpoint_id') and values.get('orderpoint_id').is_branch_order:
            location_name = values.get('orderpoint_id').location_id.display_name
            group_name = 'Manual Reorder %s' % location_name
            procurement_group = self.env["procurement.group"].search([('name', '=', group_name)])

            if procurement_group:
                move_values['group_id'] = procurement_group
            else:
                move_values['group_id'] = self.env["procurement.group"].create({'name': group_name})

            move_values['group_id'] = move_values['group_id'].id
            move_values['origin'] = group_name
            # move_values['ro_orderpoint_id'] = values.get('orderpoint_id').id

        orderpoint_id = values.get('orderpoint_id')

        if orderpoint_id and orderpoint_id.stock_move_orderpoint_id:
            move_values['stock_move_orderpoint_id'] = orderpoint_id.stock_move_orderpoint_id.id
            
        elif orderpoint_id:
            new_stock_move_op_id = self.env['stock.move.orderpoint'].create({
                'orderpoint_id': orderpoint_id.stock_move_orderpoint_id.id
            })

            orderpoint_id.stock_move_orderpoint_id = new_stock_move_op_id
            move_values['stock_move_orderpoint_id'] = new_stock_move_op_id.id
        return move_values



# To assign move after confirm
StockRule = stock.models.stock_rule.StockRule

@api.model
def _run_pull(self, procurements):
    moves_values_by_company = defaultdict(list)
    mtso_products_by_locations = defaultdict(list)

    # To handle the `mts_else_mto` procure method, we do a preliminary loop to
    # isolate the products we would need to read the forecasted quantity,
    # in order to to batch the read. We also make a sanitary check on the
    # `location_src_id` field.
    for procurement, rule in procurements:
        if not rule.location_src_id:
            msg = _('No source location defined on stock rule: %s!') % (
                rule.name, )
            raise stock.models.stock_rule.ProcurementException(
                [(procurement, msg)])

        if rule.procure_method == 'mts_else_mto':
            mtso_products_by_locations[rule.location_src_id].append(
                procurement.product_id.id)

    # Get the forecasted quantity for the `mts_else_mto` procurement.
    forecasted_qties_by_loc = {}
    for location, product_ids in mtso_products_by_locations.items():
        products = self.env['product.product'].browse(
            product_ids).with_context(location=location.id)
        forecasted_qties_by_loc[location] = {
            product.id: product.free_qty for product in products}

    # Prepare the move values, adapt the `procure_method` if needed.
    py_batch_array = {}
    picking_max = 50
    for procurement, rule in procurements:
        procure_method = rule.procure_method
        if rule.procure_method == 'mts_else_mto':
            qty_needed = procurement.product_uom._compute_quantity(
                procurement.product_qty, procurement.product_id.uom_id)
            qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
            if float_compare(qty_needed, qty_available, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                procure_method = 'make_to_stock'
                forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
            else:
                procure_method = 'make_to_order'

        # Split picking by 20 move
        if procurement.values.get('orderpoint_id') and procurement.values.get('orderpoint_id').py_batch:
            py_batch = procurement.values.get('orderpoint_id').py_batch
            py_batch_number = 0
            number = 1
            count = 1

            if not py_batch_array.get(py_batch):
                old_moves = self.env['stock.move'].search(
                    [('py_batch_source', '=', py_batch)])

                if old_moves:
                    num = len(old_moves) / picking_max
                    number = int(num) + 1
                    count = ((num - int(num)) * picking_max) + 1

                py_batch_array[py_batch] = {
                    'number': number,
                    'count': count
                }
                py_batch_number = number

            elif py_batch_array and py_batch_array.get(py_batch) and py_batch_array.get(py_batch)['count'] < picking_max:
                py_batch_array.get(py_batch)['count'] += 1
                py_batch_number = py_batch_array.get(py_batch)['number']
            else:
                py_batch_array.get(py_batch)['number'] = py_batch_array.get(
                    py_batch)['number'] + 1
                py_batch_number = py_batch_array.get(py_batch)['number']
                py_batch_array.get(py_batch)['count'] = 1

            procurement.values['py_batch'] = py_batch + \
                '/' + str(py_batch_number)
            procurement.values['py_batch_source'] = py_batch

        move_values = rule._get_stock_move_values(*procurement)
        move_values['procure_method'] = procure_method
        moves_values_by_company[procurement.company_id.id].append(move_values)

    for company_id, moves_values in moves_values_by_company.items():
        # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        moves = self.env['stock.move'].with_user(SUPERUSER_ID).with_company(company_id).create(moves_values)
        # Since action_confirm launch following procurement_group we should activate it.
        moves._action_confirm()
        # Assign from oreder point of view
        # if moves and 'OB' in moves[0].origin:
        # moves._action_assign()
    return True


StockRule._run_pull = _run_pull
