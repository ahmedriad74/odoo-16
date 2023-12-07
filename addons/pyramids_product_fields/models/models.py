# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'name'

    name = fields.Char(tracking=True)
    list_price = fields.Float(tracking=True)
    min_margin = fields.Float(
        string='Min Margin %',
        digits='Product Price'
    )
    unit_factor = fields.Integer(
        string='Unit Factor',
        default=1,
        tracking=True
    )
    unit_price = fields.Float(
        string='Unit Price',
        compute="_compute_unit_price",
        inverse="_inverse_unit_price"
    )
    availability = fields.Selection(
        string='Availability',
        selection=[
            ('available', 'Available'),
            ('shortage', 'Shortage')
        ]
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='product.contract',
        ondelete='restrict'
    )
    location = fields.Selection(
        string='Interior Location',
        selection=[
            ('shelf', 'Shelf'),
            ('refrigerator', 'Refrigerator')
        ]
    )
    status = fields.Selection(
        string='Status',
        selection=[
            ('seasonal', 'Seasonal'),
            ('urgent', 'Urgent'),
            ('pushed', 'Pushed'),
            ('normal', 'Normal')
        ]
    )
    active_ingredient = fields.Char(string='Active Ingredient') 

    # QUESTION?????
    # higest_lot_price = fields.Float(compute='_compute_higest_lot_price', string='Highest Lot Price')

    # @api.depends('tracking')
    # def _compute_higest_lot_price(self):
    #     self.higest_lot_price = 0

    #     for product in self:            
    #         if product.tracking == 'lot':
    #             product_product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
    #             # upgrade16 ==> 'stock.lot' -> 'stock.lot'
    #             product_lots = self.env['stock.lot'].search([('product_id', '=', product_product.id)])

    #             if product_lots:
    #                 product.higest_lot_price = sorted(product_lots.mapped('py_price_unit'))[-1]

    #                 if product.higest_lot_price > product.list_price:
    #                     product.list_price = product.higest_lot_price

    @api.depends('list_price', 'unit_factor')
    def _compute_unit_price(self):
        self.unit_price = 0

        for p in self:
            p.unit_price = p.list_price / p.unit_factor

    def _inverse_unit_price(self):
        for p in self:
            p.list_price = p.unit_price * p.unit_factor
