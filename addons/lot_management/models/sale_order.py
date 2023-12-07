# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def copy(self, default=None):
        raise UserError(_('Please Create New Order.'))

    def action_confirm(self):
        for order in self:

            # Remove line with zero value
            lines_to_unlink = order.order_line.filtered(lambda l: l.product_uom_qty <= 0)

            if lines_to_unlink:
                lines_to_unlink.unlink()

            if any(order.order_line.filtered(lambda l: l.free_qty_today < l.qty_to_deliver and l.display_qty_widget)):
                raise ValidationError(
                    _('Product has not enough quantity.'))
            if any(order.order_line.filtered(lambda l: not l.py_lot_id and l.product_id.tracking == 'lot')):
                raise ValidationError(
                    _('Please choose lot for product.'))
            if any(order.order_line.filtered(lambda l: (l.py_lot_id or l.product_id.tracking == 'lot') and l.product_uom_qty > l.py_location_product_lot_qty)):
                message = (
                    "Not Enough QTY for product in this lot")
                raise ValidationError(_(message))

        res = super(SaleOrder, self).action_confirm()

        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    py_search_lot_product = fields.Char('Search', store=False)
    # upgrade16 ==> 'stock.lot' -> 'stock.lot'
    py_lot_id = fields.Many2one(
        string='Lot',
        comodel_name='stock.lot',
        ondelete='restrict',
        domain="[('id','in',py_available_lot_ids)]"
    )
    py_available_lot_ids = fields.Many2many(
        string='Lot',
        comodel_name='stock.lot',
        compute='_compute_py_available_lot_ids'
    )

    py_strip_product_uom_qty = fields.Integer(string='Unit', default=0.0)
    py_box_product_uom_qty = fields.Integer(string='Quantity Box', default=0.0)
    py_location_product_lot_qty = fields.Float('Quantity Lot Location', digits='Product Unit of Measure', compute='_py_location_product_qty')

    py_location_product_lot_qty_text = fields.Text(
        'Quantity Lot Available', compute='_py_location_product_qty')
    py_location_product_all_qty_text = fields.Text(
        'Quantity Available', compute='_py_location_product_qty')

    @api.onchange('py_box_product_uom_qty', 'py_strip_product_uom_qty', 'py_lot_id')
    def _onchange_strip_box_product_uom_qty(self):
        strip_uom_factor = self.product_id.unit_factor if self.product_id else 1

        if self.product_id and self.product_id.unit_factor <= 0:
            message = 'Product %s can\'t have 0 unit factor.' % (self.product_id.name)
            raise UserError(_(message))

        if self.py_strip_product_uom_qty > strip_uom_factor - 1:
            message = 'Product can has only %s unit' % (strip_uom_factor - 1)
            raise ValidationError(_(message))

        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        strip = round(self.py_strip_product_uom_qty / strip_uom_factor, rounding)
        box = self.py_box_product_uom_qty
        self.product_uom_qty = strip + box
        available = self.py_location_product_lot_qty
        rem = round(1 - (strip * strip_uom_factor), rounding)

        if abs(round(available - int(available) - strip, rounding)) == abs(rem):
            self.product_uom_qty = self.product_uom_qty + rem

        elif abs(round(abs(int(available) - available) - abs(int(self.product_uom_qty)-self.product_uom_qty), rounding)) == abs(.0001):
            self.product_uom_qty = self.product_uom_qty - .0001

        elif abs(round(abs(int(available) - available) - abs(int(self.product_uom_qty)-self.product_uom_qty), rounding)) == abs(.0002):
            self.product_uom_qty = self.product_uom_qty - .0002

        # Check total qty of line parent and child
        if (self.py_lot_id or self.product_id.tracking == 'lot') and self.product_uom_qty > available:
            title = ("Warning for product %s") % self.product_id.name
            message = 'Not Enough QTY'
            warning = {
                'title': title,
                'message': message,
            }
            return {'warning': warning}

    @api.depends('py_lot_id', 'product_id', 'order_id.warehouse_id')
    def _py_location_product_qty(self):
        for line in self:
            # We only care for the quants in internal or transit locations.
            location = line.order_id.warehouse_id.lot_stock_id
            strip_uom_factor = line.product_id.unit_factor if line.product_id else 1
            route_location = line.route_id.rule_ids[0].location_src_id if len(line.route_id.rule_ids)>0 else False
            quants_all = line.product_id.stock_quant_ids.filtered(lambda q: (q.location_id.usage == 'internal' or
                                                                  (q.location_id.usage == 'transit' and q.location_id.company_id)) and
                                                                  q.location_id in (location, route_location))
            quants = quants_all.filtered(lambda q: q.lot_id == line.py_lot_id)
            qty_in_all_lot = sum(quants_all.mapped('available_quantity'))
            remain_qty_in_all_lot = (qty_in_all_lot - int(qty_in_all_lot)) * strip_uom_factor
            line.py_location_product_all_qty_text = '%s Qty\n%s Unit' % (
                int(qty_in_all_lot), round(remain_qty_in_all_lot, 0))

            qty_in_lot = sum(quants.mapped('available_quantity'))
            remain_qty_in_lot = (
                qty_in_lot - int(qty_in_lot)) * strip_uom_factor

            line.py_location_product_lot_qty = qty_in_lot
            line.py_location_product_lot_qty_text = '%s Qty\n%s Unit' % (int(qty_in_lot),
                                                                         round(remain_qty_in_lot, 0))

    @api.depends('py_lot_id', 'order_id.warehouse_id', 'product_id')
    def _compute_py_available_lot_ids(self):
        for line in self:
            available_lot_ids = available_lot_ids_route = []

            if line.route_id and line.product_id.tracking == 'lot':

                location = line.route_id.rule_ids[0].location_src_id if len(line.route_id.rule_ids) else False
                
                if line.product_id and location:
                    quants = self.env["stock.quant"].read_group(
                        [
                            ("product_id", "=", line.product_id.id),
                            ("location_id", "child_of", location.id),
                            ("available_quantity", ">", 0),
                            ("lot_id", "!=", False)
                        ],
                        ["lot_id"],
                        "lot_id",
                    )
                    available_lot_ids_route = [quant["lot_id"][0] for quant in quants]

            if line.order_id.warehouse_id and line.product_id.tracking == 'lot':
                location = line.order_id.warehouse_id.lot_stock_id

                if line.product_id:
                    quants = self.env["stock.quant"].read_group(
                        [
                            ("product_id", "=", line.product_id.id),
                            ("location_id", "child_of", location.id),
                            ("available_quantity", ">", 0),
                            ("lot_id", "!=", False),
                            ("lot_id.expiration_date", ">=", datetime.now())
                        ],
                        ["lot_id"],
                        "lot_id",
                    )
                    available_lot_ids = [quant["lot_id"][0] for quant in quants]
                    available_lot_ids += available_lot_ids_route
                    # remove lots in other sale order line
                    lots_in_line = line.order_id.order_line.py_lot_id.ids
                    available_lot_ids = [
                        lot for lot in available_lot_ids if lot not in lots_in_line]

                    # Get latest lot expiration date
                    if not line.py_lot_id:
                        # upgrade16 ==> 'stock.lot' -> 'stock.lot'
                        py_available_lot_ids = self.env['stock.lot'].browse(
                            available_lot_ids).sorted(key=lambda r: r.expiration_date)

                        if len(py_available_lot_ids):
                            line.py_lot_id = py_available_lot_ids[0]
                            available_lot_ids.remove(available_lot_ids[0])
                            line._onchange_py_field_lot_id()

            line.py_available_lot_ids = available_lot_ids

    @api.onchange('py_search_lot_product')
    def _onchange_py_search_lot_product(self):
        if self.py_search_lot_product:
            py_search_lot_product = self.py_search_lot_product.replace('ز', '.')
            new_barcode = py_search_lot_product.split('.')

            if len(new_barcode) > 1:
                py_search_lot_product = str(int(new_barcode[0])) + '.' + str(new_barcode[1])

            lot = self.env['stock.lot'].search([('py_barcode', '=', py_search_lot_product)])

            if lot:
                self.py_lot_id = lot
                self._onchange_py_field_lot_id()
            else:
                py_search_lot_product = py_search_lot_product.split('.')[0]
                product = self.env['product.product'].search([('default_code', '=', py_search_lot_product)])

                if product:
                    self.product_id = product
                    self.product_id_change()
                else:
                    product = self.env['product.product'].search([('barcode', '=', py_search_lot_product)])
                    if product:
                        self.product_id = product
                        self.product_id_change()
                    else:
                        title = ("No Product Found.")
                        message = 'Not Product'
                        warning = {
                            'title': title,
                            'message': message,
                        }
                        return {'warning': warning}

    def change_discount_percentage(self):
        self.discount = 0.0

        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return
        
        # upgrade16
        # product = self.product_id.with_context(
        #     lang=self.order_id.partner_id.lang,
        #     partner=self.order_id.partner_id,
        #     quantity=self.product_uom_qty,
        #     date=self.order_id.date_order,
        #     pricelist=self.order_id.pricelist_id.id,
        #     uom=self.product_uom.id,
        #     fiscal_position=self.env.context.get('fiscal_position')
        # )
        product_context = dict(
            self.env.context, 
            partner_id=self.order_id.partner_id.id,
            date=self.order_id.date_order,
            uom=self.product_uom.id
            )
        # upgrade16 ==> 'get_product_price_rule' => '_get_product_price_rule'
        # upgrade16==> '_get_real_price_currency' => '_get_pricelist_price_before_discount'
        # new_list_price, currency = self.with_context(product_context)._get_real_price_currency(
        #                         product, rule_id, self.product_uom_qty, self.product_uom, 
        #                         self.order_id.pricelist_id.id)
        price, rule_id = self.order_id.pricelist_id.with_context(product_context)._get_product_price_rule(
                                self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        new_list_price = self._get_pricelist_price_before_discount()
        currency = self.currency_id

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, 
                    self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, 
                    self.order_id.date_order or fields.Date.today()
                    )
            
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount

    @api.onchange('py_lot_id')
    def _onchange_py_field_lot_id(self):
        if self.order_id.state not in ('done', 'sale'):
            if self.py_lot_id and not self.product_id:
                self.product_id = self.py_lot_id.product_id
                self.product_id_change()
                self.product_uom_change()
                self.change_discount_percentage()
            else:
                self.product_id_change()
                self.product_uom_change()

                if self.order_id.pricelist_id and self.order_id.pricelist_id.is_depend_on_cost:
                    self.price_unit = self.product_id.standard_price
                elif self.product_id.categ_id and self.product_id.categ_id.lot_be_highest_price:
                    self.price_unit = self.product_id.lst_price
                else:
                    self.price_unit = self.py_lot_id.py_price_unit
                
                self.change_discount_percentage()

    # upgrade16 ==> 'product_id_change' doesn't exist more in V16
    @api.onchange("product_id")
    def product_id_change(self):
        # set unit price before select customer
        self.price_unit = self.product_id.lst_price
        # result = super().product_id_change()
        # to set product qty at first
        if int(self.py_location_product_lot_qty) == 0 and float(self.py_location_product_lot_qty) > 0:
            self.product_uom_qty = 1 / self.product_id.unit_factor
            self.py_box_product_uom_qty = 0
            self.py_strip_product_uom_qty = 1
        else:
            self.py_box_product_uom_qty = 1
            self.product_uom_qty = 1
            self.py_strip_product_uom_qty = 0

        if self.py_lot_id.product_id != self.product_id:
            self.py_lot_id = False

        elif self.py_lot_id:
            self.price_unit = self.py_lot_id.py_price_unit

        if self.order_id.pricelist_id and self.order_id.pricelist_id.is_depend_on_cost:
            self.price_unit = self.product_id.standard_price

        self.change_discount_percentage()
        # return result

    # upgrade16 ==> 'product_uom_change' become '_compute_price_unit'
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        # super().product_uom_change()
        if self.py_lot_id:
            self.price_unit = self.py_lot_id.py_price_unit
            if self.order_id.pricelist_id and self.order_id.pricelist_id.is_depend_on_cost:
                self.price_unit = self.product_id.standard_price
            self.change_discount_percentage()

