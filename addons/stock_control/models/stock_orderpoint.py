# -*- coding: utf-8 -*-

import math
from odoo import SUPERUSER_ID, _, api, models, fields
from odoo.tools import float_compare
from datetime import timedelta, datetime
from odoo.addons import stock

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    stock_move_orderpoint_id = fields.One2many('stock.move.orderpoint', 'orderpoint_id')    

    def message_to_stock_control(self, message, user=None):
        channel = self.env.ref('stock_control.channel_stock_control')
        # bot user for auto order
        if user is None:
            user = self.env['res.users'].browse(SUPERUSER_ID)

        channel.message_post(
            body=message, subtype_xmlid='mail.mt_comment', partner_ids=[user.partner_id.id])

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.env.user.has_group('stock.group_stock_manager') and not self.py_batch:
            team = self.env['crm.team'].search(
                [('member_ids', '=', self.env.user.id)])
            warehouse = self.env['stock.warehouse'].search(
                [('crm_team_id', '=', team.id)], limit=1)

            self.location_id = warehouse.lot_stock_id
            self.warehouse_id = warehouse

    @api.model_create_multi
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        if 'py_batch' not in values:
            team = self.env['crm.team'].search(
                [('member_ids', '=', self.env.user.id)])
            warehouse = self.env['stock.warehouse'].search(
                [('crm_team_id', '=', team.id)], limit=1)

            buy_route = self.env['stock.route'].search([
                ('used_warehouse_id', '=', warehouse.id),
                ('py_is_reorder_route', '=', True),
                ('py_is_buy_route', '=', True)
            ])

            values['is_branch_order'] = True
            values['warehouse_id'] = warehouse.id
            values['location_id'] = warehouse.lot_stock_id.id
            values['route_id'] = buy_route.id

        return super().create(values)

    # For create new picking on manual reorder
    def action_replenish(self):
        self._procure_orderpoint_confirm(company_id=self.env.company)
        now = datetime.now()
        notification = False

        if len(self) == 1:
            notification = self._get_replenishment_order_notification(now)
        # Forced to call compute quantity because we don't have a link.
        self._compute_qty()

        # SO Branch Can use it
        if self[0].is_branch_order:
            self.message_to_stock_control('Manual replenishment created.')

        return notification

    # To Remove auto create order point
    # TODO get qty from po etc.
    @api.model
    def action_open_orderpoints(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_orderpoint_replenish")
        action['context'] = self.env.context
        return action
        # return self._get_orderpoint_action()

    # Automatic
    @api.model
    def _auto_consumption(self, company_id):
        company = self.env['res.company'].browse(company_id)
        days_before = company.days_before
        today_day = datetime.now()
        end_date = today_day.date() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_before)
        main_location = self.env['stock.location'].search(
            [('ro_is_main_location', '=', True), ('usage', '=', 'internal')], order='id asc', limit=1)

        self._cr.execute("""delete from stock_consumption_rate""")
        self._cr.execute("""
            INSERT INTO 
                stock_consumption_rate
                    (
                        product_id, 
                        location_id, 
                        warehouse_id, 
                        route_id, 
                        qty_on_hand, 
                        qty_forecast, 
                        total, 
                        is_main_location, 
                        company_id, 
                        categ_id, 
                        levela_id,
                        batch_name_part, 
                        purchase_requisition, 
                        rate, 
                        start_date, 
                        end_date, 
                        days,
                        write_uid, 
                        create_uid, 
                        write_date, 
                        create_date
                    )
            SELECT 
                main_query.product_id, 
                main_query.location_id, 
                warehouse_id, route_id, 
                sq_query.quantity,
                ROUND(COALESCE(sq_query.quantity,0) + COALESCE(virtual_move_available,0)), 
                total,
                is_main_location, 
                main_query.company_id, 
                categ_id, levela_id, 
                batch_name_part, 
                purchase_requisition, 
                rate, 
                '{}','{}',{},{},{},'{}','{}'
            FROM 
                (
                SELECT * 
                FROM 
                    (
            			SELECT *, (total/{})*30 AS rate 
                        FROM (
                            SELECT 
                                aml.product_id, 
                                aml.location_id, 
                                sl.py_warehouse_id AS warehouse_id, 
                                slr.id AS route_id,
                                SUM(mls.quantity_for_consumption) AS total, 
                                False AS is_main_location, 
                                am.company_id, 
                                pt.categ_id, 
                                pt.levela_id,
                                CASE WHEN pt.levela_id is not null THEN concat('/', aml.location_id, '/', lvla.name)
                                ELSE concat('/', aml.location_id, '/', 'Other') END AS batch_name_part, 
                                pt.purchase_requisition
                            FROM 
                                account_move_line aml  
                            LEFT JOIN
                                (
                                    SELECT id,CASE
                                    WHEN move_type = 'out_invoice' THEN quantity
                                    WHEN move_type = 'out_refund' THEN -quantity
                                    ELSE 0
                                    END AS quantity_for_consumption FROM account_move_line aml
                                    WHERE aml.date >= '{}' 
                                    AND aml.date <= '{}' 
                                    AND aml.company_id = {}
                                    AND aml.location_id  != {} 
                                    AND aml.location_id is not null
                                ) AS mls on mls.id = aml.id
                            LEFT JOIN 
                                product_product pp on aml.product_id = pp.id 
                            LEFT JOIN 
                                product_template pt on pt.id = pp.product_tmpl_id 
                            LEFT JOIN 
                                account_account aa on aml.account_id = aa.id 
                            LEFT JOIN 
                                account_move am on am.id = aml.move_id
                            LEFT JOIN 
                                stock_location sl on sl.id = aml.location_id
                            LEFT JOIN 
                                product_levela lvla on lvla.id = pt.levela_id
                            LEFT JOIN 
                                stock_location_route slr 
                            ON 
                                slr.used_warehouse_id = sl.py_warehouse_id 
                            AND 
                                py_is_buy_route = True 
                            AND 
                                py_is_reorder_route = True
                            WHERE 
                                pt.type = 'product' 
                            AND 
                                aml.date >= '{}' 
                            AND
                                aml.date <= '{}' 
                            AND 
                                aml.company_id = {}
                            AND 
                                aml.location_id  != {} 
                            AND 
                                aml.location_id is not null
                            AND 
                                aa.internal_group = 'income' 
                            AND 
                                am.move_type in ('out_invoice','out_refund') 
                            AND 
                                am.state in ('draft', 'posted')
                            AND 
                                pp.active = true 
                            GROUP BY 
                                aml.product_id, 
                                aml.location_id, 
                                am.company_id, 
                                pt.categ_id, 
                                sl.py_warehouse_id, 
                                pt.levela_id, 
                                slr.id, 
                                lvla.name, 
                                pt.purchase_requisition 
                        )  AS branch_cons 
                
                        UNOIN ALL 
              
                        SELECT *, (total/{})*30 AS rate 
                        FROM (
                            SELECT 
                                aml.product_id, {} AS location_id, 
                                {} AS warehouse_id, 
                                slr.id AS route_id,
                                SUM(mls.quantity_for_consumption ) AS total, 
                                True AS is_main_location, 
                                am.company_id, 
                                pt.categ_id,
                                 pt.levela_id,
                                CASE WHEN pt.levela_id is not null THEN concat('/{}/', lvla.name) ELSE concat('/{}/', 'Other') END AS batch_name_part,
                                pt.purchase_requisition
                            FROM 
                                account_move_line aml  
                            LEFT JOIN 
                                (
                                    SELECT id,
                                    CASE WHEN move_type = 'out_invoice' THEN quantity
                                        WHEN move_type = 'out_refund' THEN -quantity
                                        ELSE 0
                                        END AS quantity_for_consumption FROM  account_move_line aml
                                    WHERE 
                                        aml.date >= '{}' 
                                    AND 
                                        aml.date <= '{}' 
                                    AND 
                                        aml.company_id = {}
                                    AND
                                        aml.location_id  != {}
                                    AND 
                                        aml.location_id is not null
                                ) AS mls on mls.id = aml.id
                            LEFT JOIN 
                                product_product pp 
                            ON 
                                aml.product_id = pp.id 
                            LEFT JOIN 
                                product_template pt 
                            ON 
                                pt.id = pp.product_tmpl_id 
                            LEFT JOIN 
                                account_account aa 
                            ON 
                                aml.account_id = aa.id 
                            LEFT JOIN 
                                account_move am 
                            ON 
                                am.id = aml.move_id
                            LEFT JOIN 
                                product_levela lvla 
                            ON 
                                lvla.id = pt.levela_id
                            LEFT JOIN 
                                stock_location_route slr 
                            ON 
                                slr.used_warehouse_id = {}
                            AND 
                                py_is_buy_route = True 
                            AND 
                                py_is_reorder_route = True
                            WHERE 
                                pt.type = 'product' 
                            AND 
                                aml.date >= '{}' 
                            AND 
                                aml.date <= '{}' 
                            AND 
                                aml.company_id = {}
                            AND 
                                aml.location_id  != {} 
                            AND 
                                aml.location_id is not null
                            AND 
                                aa.internal_group = 'income' 
                            AND 
                                am.move_type in ('out_invoice','out_refund') 
                            AND 
                                am.state in ('draft', 'posted')
                            AND 
                                pp.active = true 
                            GROUP BY 
                                aml.product_id,
                                am.company_id, 
                                pt.categ_id,
                                pt.levela_id, 
                                slr.id, 
                                lvla.name, 
                                pt.purchase_requisition 
                        ) AS main_cons 
                    ) AS total_cons
                ) AS main_query
                          
				LEFT JOIN 
                    (
                        SELECT 
                            product_id, 
                            location_id, 
                            SUM(quantity) AS quantity 
                        FROM 
                            stock_quant 
                        GROUP BY 
                            product_id, location_id
                    ) AS sq_query 
                ON 
                    sq_query.product_id = main_query.product_id 
                AND 
                    sq_query.location_id = main_query.location_id

                LEFT JOIN 
                    (
                        SELECT 
                            total_move.product_id AS product_sub_id, 
                            total_move.location_dest_id,
                            SUM(total_move.quantity) AS virtual_move_available
                        FROM 
                            product_product pp 
                        LEFT JOIN 
                            (
                                SELECT 
                                    move_in.product_id, 
                                    move_in.location_dest_id,
                                    COALESCE(move_out.qty_out,0) + COALESCE(move_in.qty_in, 0) AS quantity
                                FROM 
                                    (
                                        SELECT 
                                            product_id, 
                                            location_dest_id,
                                            SUM(product_qty) AS qty_in
                                        FROM 
                                            stock_move
                                        WHERE 
                                            state in ('waiting', 'confirmed', 'assigned', 'partially_available') 
                                        GROUP BY 
                                            product_id ,location_dest_id 
                                    ) AS move_in
                                LEFT JOIN
                                    (
                                        SELECT 
                                            product_id, 
                                            location_id, 
                                            SUM(product_qty) * -1 AS qty_out
                                        FROM 
                                            stock_move
                                        WHERE 
                                            state in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                        GROUP BY
                                            product_id ,location_id 
                                    ) as move_out
                                ON 
                                    move_in.product_id = move_out.product_id 
                                AND 
                                    move_out.location_id = move_in.location_dest_id 

                                UNION 

                                SELECT 
                                    move_out.product_id, 
                                    move_out.location_id , 
                                    COALESCE(move_out.qty_out,0) + COALESCE(move_in.qty_in,0) AS quantity
                                FROM 
                                    (
                                        SELECT 
                                            product_id, 
                                            location_id, SUM(product_qty) * -1 AS qty_out
                                        FROM
                                            stock_move
                                        WHERE 
                                            state in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                        GROUP BY 
                                            product_id ,location_id 
                                    ) as move_out
                                LEFT JOIN 
                                    (
                                        SELECT 
                                            product_id, location_dest_id , 
                                            SUM(product_qty) AS qty_in
                                        FROM 
                                            stock_move
                                        WHERE 
                                            state in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                        GROUP BY 
                                            product_id ,location_dest_id 
                                    ) AS move_in
                                    ON 
                                        move_in.product_id = move_out.product_id 
                                    AND 
                                        move_out.location_id = move_in.location_dest_id 
                            ) AS total_move 
                            ON 
                                total_move.product_id = pp.id
                            GROUP BY 
                                total_move.product_id, 
                                total_move.location_dest_id
                    ) AS sub_query 
                    ON 
                        sub_query.product_sub_id = main_query.product_id 
                    AND 
                        sub_query.location_dest_id = main_query.location_id
        """.format(
                start_date, 
                end_date, 
                days_before, 
                SUPERUSER_ID, 
                SUPERUSER_ID, 
                today_day, 
                today_day,
                days_before, 
                start_date, 
                end_date, 
                company.id, 
                main_location.id, 
                start_date, 
                end_date, 
                company.id,
                main_location.id, 
                days_before, 
                main_location.id,
                main_location.py_warehouse_id.id,
                main_location.id, 
                main_location.id, 
                start_date, 
                end_date, 
                company.id, 
                main_location.id, 
                main_location.py_warehouse_id.id,
                start_date, 
                end_date, 
                company.id, 
                main_location.id
            ))

        self.message_to_stock_control(
            'Consumption created for {}.'.format(today_day))

    @api.model
    def _auto_orderpoint(self, company_id):
        self._cr.execute("""delete from stock_warehouse_orderpoint""")
        py_batch = self.env['ir.sequence'].next_by_code(
            'stock.warehouse.orderpoint.batch')
        company = self.env['res.company'].browse(company_id)
        today_day = datetime.now()
        except_levela_ids = company.except_levela_ids
        except_products = self.env['product.product'].search(
            [('levela_id', 'in', except_levela_ids.ids)])
        main_location = self.env['stock.location'].search(
            [('ro_is_main_location', '=', True), ('usage', '=', 'internal')], order='id asc', limit=1)
        product_min_duration_branch = company.product_min_duration_branch
        product_max_duration_branch = company.product_max_duration_branch
        product_min_duration_main = company.product_min_duration_main
        product_max_duration_main = company.product_max_duration_main

        #TODO:  product_id not in {} is bad query when there are not exception category also remove all exception
        #category can't be done

        self._cr.execute(""" 
            Insert INTO 
                stock_warehouse_orderpoint 
            (
                write_uid, 
                create_uid, 
                write_date, 
                create_date, 
                product_min_qty,
                product_max_qty, 
                start_date, 
                end_date,
                product_category_id, 
                product_id, 
                rate,
                route_id,
                warehouse_id, 
                location_id, 
                qty_to_order, 
                qty_on_hand, 
                levela_id, 
                company_id, 
                py_batch, 
                name, 
                trigger, 
                is_branch_order, 
                qty_multiple, 
                active
            )
            SELECT
                '{}','{}','{}','{}',
                CASE WHEN location_id != {} Then ceil((rate/30)*{}) ELSE ceil((rate/30)*{}) END as product_min_qty,
                CASE WHEN location_id != {} Then ceil((rate/30)*{}) ELSE ceil((rate/30)*{}) END as product_max_qty,
                start_date, 
                end_date, 
                categ_id, 
                product_id, 
                rate, 
                route_id, 
                warehouse_id, 
                location_id,
                CASE WHEN qty_on_hand < CASE WHEN location_id != {} Then ceil((rate/30)*{}) ELSE ceil((rate/30)*{}) END
                THEN
                CASE WHEN location_id != {} Then ceil((rate/30)*{}) ELSE ceil((rate/30)*{}) END - floor(qty_on_hand)
                ESLE 0
                END, 
                qty_on_hand, 
                levela_id, 
                company_id, CONCAT('{}', batch_name_part),
                CONCAT('{}', batch_name_part), 'manual', False, 1, True 
            FROM 
                stock_consumption_rate
            where 
                product_id not in {} 
            AND 
                purchase_requisition = 'tenders'
            """.format(SUPERUSER_ID, SUPERUSER_ID, today_day, today_day, main_location.id, product_min_duration_branch,
                       product_min_duration_main, main_location.id,
                       product_max_duration_branch, product_max_duration_main, main_location.id,
                       product_min_duration_branch, product_min_duration_main, main_location.id,
                       product_max_duration_branch, product_max_duration_main, py_batch, py_batch,
                       tuple(except_products.ids)))

        self.message_to_stock_control(
            'Reorder created for {} batch number {}.'.format(today_day, py_batch))

    # Automatic
    @api.model
    def _autoreorder_orderpoint(self, company_id):
        company = self.env['res.company'].browse(company_id)
        # Get locations to run today
        today_day_datetime = datetime.now()
        today_day = today_day_datetime.strftime("%A")
        day_location = company.day_location_ids.filtered(
            lambda day_loc: day_loc.day_name == today_day.lower())
        to_reorder_location = day_location.location_ids
        main_location = self.env['stock.location'].search(
            [('ro_is_main_location', '=', True), ('usage', '=', 'internal')], order='id asc', limit=1)
        all_records = self.search(
            [('is_branch_order', '=', False), ('company_id', '=', company.id), ('location_id', '!=', main_location.id)])
        records = all_records.filtered(
            lambda point: point.location_id.id in to_reorder_location.ids)

        if not day_location:
            all_records.write(
                {'name': 'Manual Reorder', 'py_batch': 'Manual Reorder', 'is_branch_order': True})
            return

        for ids in self._cr.split_for_in_conditions(records.ids, size=1000):
            current_records = self.browse(ids)
            current_records.action_replenish()
            current_records.write(
                {'name': 'Manual Reorder', 'py_batch': 'Manual Reorder', 'is_branch_order': True})
            self._cr.commit()

        if all_records:
            all_records.write(
                {'name': 'Manual Reorder', 'py_batch': 'Manual Reorder', 'is_branch_order': True})
            self.message_to_stock_control(
                'Internal transfer created for {}.'.format(today_day_datetime))

    @api.model
    def _autoreorder_orderpoint_buy(self, company_id):
        company = self.env['res.company'].browse(company_id)
        # Get locations to run today
        today_day_datetime = datetime.now()
        today_day = today_day_datetime.strftime("%A")
        day_location = company.day_location_ids.filtered(
            lambda day_loc: day_loc.day_name == today_day.lower())
        main_location = self.env['stock.location'].search(
            [('ro_is_main_location', '=', True), ('usage', '=', 'internal')], order='id asc', limit=1)
        records = self.search(
            [('company_id', '=', company.id), ('is_branch_order', '=', False), ('location_id', '=', main_location.id)])

        if not day_location:
            records.unlink()
            return

        for ids in self._cr.split_for_in_conditions(records.ids, size=1000):
            currnt_records = self.browse(ids)
            currnt_records.action_replenish()
            currnt_records.unlink()
            self._cr.commit()

        if records:
            self.message_to_stock_control(
                'Tender created for {}.'.format(today_day_datetime))

@api.depends('qty_multiple', 'qty_on_hand', 'product_min_qty', 'product_max_qty')
def _compute_qty_to_order(self):
    for orderpoint in self:
        if not orderpoint.product_id or not orderpoint.location_id:
            orderpoint.qty_to_order = False
            continue
        qty_to_order = 0.0
        rounding = orderpoint.product_uom.rounding
        if float_compare(orderpoint.qty_on_hand, orderpoint.product_min_qty, precision_rounding=rounding) < 0:
            qty_to_order = max(orderpoint.product_min_qty, orderpoint.product_max_qty) - math.floor(orderpoint.qty_on_hand)

            remainder = orderpoint.qty_multiple > 0 and qty_to_order % orderpoint.qty_multiple or 0.0
            if float_compare(remainder, 0.0, precision_rounding=rounding) > 0:
                qty_to_order += orderpoint.qty_multiple - remainder
        orderpoint.qty_to_order = qty_to_order


stock.models.stock_orderpoint.StockWarehouseOrderpoint._compute_qty_to_order = _compute_qty_to_order