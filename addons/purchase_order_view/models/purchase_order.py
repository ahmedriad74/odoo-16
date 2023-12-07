# -*- coding: utf-8 -*-

from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_cancel_orders(self):
        domain = self._context.get('active_domain')
        if len(domain) and domain[0][0] == 'requisition_id':
            orders_to_cancel = self.browse(self._context.get('active_ids'))
            orders_to_cancel.state = 'cancel'
            