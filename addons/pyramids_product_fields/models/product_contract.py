# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductContract(models.Model):
    _name = 'product.contract'
    _description = 'Product Contract'
    _rec_name = "name"

    name = fields.Char('Name')
    