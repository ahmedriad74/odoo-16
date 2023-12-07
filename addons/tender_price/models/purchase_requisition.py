# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
    
    price_unit = fields.Float(string='Cost')