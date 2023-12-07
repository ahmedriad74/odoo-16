# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import UserError


class StockconsumptionRate(models.Model):
    _name = 'stock.consumption.rate'
    _description = 'Consumption Rate'
    _check_company_auto = True
    _rec_name = "product_id"
    
    rate = fields.Float('Rate', readonly=True)
    total = fields.Float('Total', readonly=True)
    days = fields.Float('Days', readonly=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', ondelete="cascade", required=True, check_company=True, readonly=True)
    warehouse_id = fields.Many2one(related='location_id.py_warehouse_id', store=True)
    product_tmpl_id = fields.Many2one(
        'product.template', related='product_id.product_tmpl_id')
    categ_id = fields.Many2one(
        'product.category', 'Product Category', related='product_tmpl_id.categ_id', store=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        ondelete='cascade', required=True, check_company=True, readonly=True)
    internal_ref = fields.Char(related='product_id.default_code')
    ro_barcode = fields.Char(related='product_id.barcode')
    product_name = fields.Char(related='product_id.name')
    # upgrade16
    # purchase_requisition = fields.Selection(related='product_id.purchase_requisition', store=True)
    levela_id = fields.Many2one(related='product_id.levela_id', store=True)
    item_comapny_id = fields.Many2one(related='product_id.item_comapny_id')
    vendor_id = fields.Many2one(related='product_id.vendor_id')
    start_date = fields.Date(string='Start Date', required=True, readonly=True)
    end_date = fields.Date(string='End Date', required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    warehouse_team_id = fields.Many2one(
        comodel_name='crm.team', string='Warehouse Team', related='location_id.warehouse_team_id')
    # upgrade16 ==> 'stock.location.route' --> 'stock.route'
    route_id = fields.Many2one(
        'stock.route', string='Preferred Route')
    py_location_product_qty = fields.Float(
        'Warehouse Stock', digits='Product Unit of Measure', compute='_py_location_product_qty')
    py_location_product_qty_main = fields.Float(
        'Branches Stock', digits='Product Unit of Measure', compute='_py_location_product_qty')
    is_main_location = fields.Boolean(string="Main Location", related='location_id.ro_is_main_location', store=True)
    list_price = fields.Float(related='product_id.list_price')
    standard_price = fields.Float(related='product_id.standard_price')
    batch_name_part = fields.Char()
    qty_on_hand = fields.Float('On Hand', readonly=True)
    qty_forecast = fields.Float('Forecast', readonly=True)
    damage_plus_expired_qty = fields.Float('Damage & Expired', compute='_py_location_product_qty')
    on_hand_by_rate = fields.Float(compute='_compute_onhand_by_rate')
    ro_on_hand_by_rate = fields.Float('On Hand/Rate')

    @api.depends('qty_on_hand', 'rate')
    def _compute_onhand_by_rate(self):
        self.on_hand_by_rate = 0
        
        for rec in self:
            if rec.rate > 0:
                rec.on_hand_by_rate = rec.qty_on_hand / rec.rate
                rec.ro_on_hand_by_rate = rec.on_hand_by_rate

    # TODO: Need to add this function in product as it's duplicated in sales order line/product get name
    @api.depends('product_id', 'location_id')
    def _py_location_product_qty(self):
        main_wh = self.env['stock.warehouse'].search([('is_main_wh', '=', True)])
        main_wh_main_location = main_wh.lot_stock_id

        for line in self:
            line.damage_plus_expired_qty = sum(line.product_id.stock_quant_ids.filtered(lambda q: q.location_id.is_expire
                                                                                            or q.location_id.is_damage).mapped('available_quantity'))
            is_main_location = line.is_main_location
            quants_all = line.product_id.stock_quant_ids.filtered(lambda q: (q.location_id.usage == 'internal' or
                                                                  (q.location_id.usage == 'transit' and q.location_id.company_id)) and
                                                                  q.location_id == line.location_id)
            dsd_loc_qty = sum(line.product_id.stock_quant_ids.filtered(lambda q: q.location_id.is_dsd).mapped('available_quantity'))
            wh_loc_qty = sum(line.product_id.stock_quant_ids.filtered(lambda q: q.location_id == main_wh_main_location).mapped('available_quantity'))
            # qty_in_location = sum(quants_all.mapped('quantity')) 
            
            if not is_main_location:
                line.py_location_product_qty =  wh_loc_qty + dsd_loc_qty
                line.py_location_product_qty_main = 0
            else:
                line.py_location_product_qty = wh_loc_qty + dsd_loc_qty
                all_qty = line.product_id.stock_quant_ids.filtered(lambda q: (q.location_id.usage == 'internal' or
                                                                            (q.location_id.usage == 'transit' and q.location_id.company_id)))
                line.py_location_product_qty_main = sum(
                    all_qty.mapped('available_quantity')) - line.damage_plus_expired_qty - line.py_location_product_qty
                    
