# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, SUPERUSER_ID


class StockReorderSettingLine(models.TransientModel):
    _name = 'stock.reorder.setting.line'
    _description = 'Stock Reorder Setting Line'

    wizard_id = fields.Many2one(
        'stock.reorder.setting', string="Wizard")
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)

    location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Locations',
        domain=[('usage', '=', 'internal')],
        required=True

    )
    day_name = fields.Selection(
        string='Day Name',
        required=True,
        selection=[('sunday', 'Sunday'), ('monday', 'Monday'),
                   ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
                   ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')]
    )


class StockReorderSetting(models.Model):
    _name = 'stock.reorder.setting'
    _description = 'Stock Reorder Setting'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    except_levela_ids = fields.Many2many(
        string='Except Level A',
        comodel_name='product.levela',
        readonly=False,
        compute='_compute_fields',
        store=True
    )
    day_location_ids = fields.One2many(
        string='Day Location',
        comodel_name='stock.reorder.setting.line',
        inverse_name='wizard_id',
        readonly=False, compute='_compute_fields', store=True
    )
    days_before = fields.Integer(
        string='Days Before', compute='_compute_fields', readonly=False, store=True)
    product_min_duration_branch = fields.Integer(
        string='Min Duration Branch', compute='_compute_fields', readonly=False, store=True)
    product_max_duration_branch = fields.Integer(
        string='Max Duration Branch',  compute='_compute_fields', readonly=False, store=True)
    product_min_duration_main = fields.Integer(
        string='Min Duration Main',  compute='_compute_fields', readonly=False, store=True)
    product_max_duration_main = fields.Integer(
        string='Max Duration Main', compute='_compute_fields', readonly=False, store=True)

    @api.depends('company_id')
    def _compute_fields(self):
        for record in self:
            day_locations = []
            company_day_location_ids = record.company_id.day_location_ids
            for day_location in company_day_location_ids:
                day_locations.append({
                    'location_ids': day_location.location_ids.ids,
                    'day_name': day_location.day_name
                })

            if day_locations:
                self.env['stock.reorder.setting.line'].search([]).unlink()
                day_locations_created = self.env['stock.reorder.setting.line'].create(
                    day_locations)

                record.day_location_ids = day_locations_created.ids
            else:
                record.day_location_ids = False

            record.days_before = record.company_id.days_before
            record.except_levela_ids = record.company_id.except_levela_ids.ids
            record.product_min_duration_branch = record.company_id.product_min_duration_branch
            record.product_max_duration_branch = record.company_id.product_max_duration_branch
            record.product_min_duration_main = record.company_id.product_min_duration_main
            record.product_max_duration_main = record.company_id.product_max_duration_main

    def save_setting(self):
        day_locations = []

        for day_location in self.day_location_ids:
            day_locations.append({
                'location_ids': day_location.location_ids.ids,
                'day_name': day_location.day_name
            })

        if day_locations:
            self.env['stock.day.locations'].search([]).with_user(SUPERUSER_ID).unlink()
            day_locations_created = self.env['stock.day.locations'].with_user(SUPERUSER_ID).create(
                day_locations)

        self.company_id.with_user(SUPERUSER_ID).write({
            'days_before': self.days_before,
            'except_levela_ids': self.except_levela_ids.ids,
            'day_location_ids': day_locations_created.ids,
            'product_min_duration_branch': self.product_min_duration_branch,
            'product_max_duration_branch': self.product_max_duration_branch,
            'product_min_duration_main': self.product_min_duration_main,
            'product_max_duration_main': self.product_max_duration_main
        })
