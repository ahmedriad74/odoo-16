# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class StockDayLocations(models.Model):
    _name = 'stock.day.locations'
    _description = 'Stock Day Locations'

    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Locations',
        domain=[('usage','=','internal')]
    )
    day_name = fields.Selection(
        string='Day Name',
        selection=[('sunday', 'Sunday'), ('monday', 'Monday'),
                   ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
                   ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')]
    )

    _sql_constraints = [
        (
            'day_name_unique',
            'unique(day_name, company_id)',
            _('Name Exist.')
        )
    ]
