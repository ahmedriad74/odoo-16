# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        for order in self:
            shortfall_lines = order.order_line.filtered(lambda line: line.product_id.is_shortfall or line.product_id.is_cosmo_shortfall)

            unique_products = dict()

            for line in shortfall_lines:
                if line.product_id in unique_products or line.product_uom_qty > 1:
                    raise ValidationError(f"You cannot sell more than one unit of '{line.product_id.name.strip()}'.")
                else:
                    unique_products[line.product_id] = True

            if  shortfall_lines and order.amount_total < 100:
                raise ValidationError('Total amount must be equal or more than 100 EGP.')
        
        return super(SaleOrder, self).action_confirm()