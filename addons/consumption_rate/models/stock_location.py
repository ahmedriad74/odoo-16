# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    warehouse_team_id = fields.Many2one(
        'crm.team', string='Warehouse Team', compute='_compute_warehouse_team_id', store=True, readonly=False)
    py_warehouse_id = fields.Many2one(
        'stock.warehouse', string='Location Warehouse', compute='_compute_warehouse_team_id', store=True, readonly=False)
    ro_is_main_location = fields.Boolean(compute='_compute_warehouse_team_id', store=True)
    is_damage = fields.Boolean('Is Damage')
    is_expire = fields.Boolean('Is Expire')
    is_dsd = fields.Boolean('Is DSD')

    # upgrade16 ==> add this method from V14
    @api.returns('stock.warehouse', lambda value: value.id)
    def get_warehouse(self):
        """ Returns warehouse id of warehouse that contains location """
        domain = [('view_location_id', 'parent_of', self.ids)]
        return self.env['stock.warehouse'].search(domain, limit=1)

    @api.depends("name")
    def _compute_warehouse_team_id(self):
        for location in self:

            location.warehouse_team_id = False
            location.py_warehouse_id = False
            location.ro_is_main_location = False
            warehouse_id = location.get_warehouse()

            if warehouse_id:
                location.warehouse_team_id = warehouse_id.crm_team_id
                location.py_warehouse_id = warehouse_id
                location.ro_is_main_location = True if not warehouse_id.parent_warehouse_id else False
