# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    days_before = fields.Integer(string='Days Before', default=90)
    except_levela_ids = fields.Many2many(
        string='Except Level A',
        comodel_name='product.levela'
    )
    day_location_ids = fields.One2many(
        string='Day Location',
        comodel_name='stock.day.locations',
        inverse_name='company_id',
    )
    product_min_duration_branch = fields.Integer(
        string='Min Duration Branch', default=7)
    product_max_duration_branch = fields.Integer(
        string='Max Duration Branch', default=15)
    product_min_duration_main = fields.Integer(
        string='Min Duration Main', default=5)
    product_max_duration_main = fields.Integer(
        string='Max Duration Main', default=10)
