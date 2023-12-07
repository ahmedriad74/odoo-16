# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
        
class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin = fields.Float('Margin', groups="base.group_system")
