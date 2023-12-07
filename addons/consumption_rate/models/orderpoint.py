# -*- coding: utf-8 -*-

from odoo import models, fields, _, api

class StockWarehouseOrderpoint(models.Model):
    _name = 'stock.warehouse.orderpoint'
    _order = "levela_id, product_id, location_id,company_id,id"
    _inherit = ['stock.warehouse.orderpoint','mail.thread', 'mail.activity.mixin']
    
    py_batch = fields.Char(string='Reorder Batch', readonly=True, index=True)
    levela_id = fields.Many2one(related='product_id.levela_id', store=True)
    start_date = fields.Date(string='Start Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    qty_to_order = fields.Float("System Order")
    warehouse_team_id = fields.Many2one(comodel_name='crm.team', string='Warehouse Team', related='location_id.warehouse_team_id')
    is_branch_order = fields.Boolean()
    qty_on_hand = fields.Float(store=True)
    rate = fields.Float('Rate', readonly=True)
    on_hand_by_rate = fields.Float(compute='_compute_onhand_by_rate')
    ro_on_hand_by_rate = fields.Float('On Hand/Rate')

    #TODO
    '''def _search_upper(self, operator, value):
        if operator == 'like':
            operator = 'ilike'
        return [('name', operator, value)]'''

    @api.depends('qty_on_hand', 'rate')
    def _compute_onhand_by_rate(self):
        self.on_hand_by_rate = 0
        
        for rec in self:
            if rec.rate > 0:
                rec.on_hand_by_rate = rec.qty_on_hand / rec.rate
                rec.ro_on_hand_by_rate = rec.on_hand_by_rate

    
