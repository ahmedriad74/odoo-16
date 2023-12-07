# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    street = fields.Char(related='partner_id.street', readonly=False, store=True)
    py_landmark = fields.Char(related='partner_id.py_landmark', readonly=False, store=True)
    city = fields.Char(related='partner_id.city', readonly=False, store=True)
    state_id = fields.Many2one(related='partner_id.state_id', readonly=False, store=True)
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False, store=True)
