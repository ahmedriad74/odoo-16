# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    order_payment_type = fields.Selection(
        string='Payment Type',
        related='pricelist_id.order_payment_type'
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        
        invoice_vals['order_payment_type'] = self.order_payment_type

        return invoice_vals