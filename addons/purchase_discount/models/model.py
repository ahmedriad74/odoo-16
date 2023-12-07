
from odoo import fields, models, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    price = fields.Float(string="Price")
    cost = fields.Float(related='product_id.standard_price')
    final_unit_cost = fields.Float('Final Unit Cost', compute='compute_final_unit_cost')
    first_discount_percent = fields.Float("Fisrt Discount")
    second_discount_percent = fields.Float("Second Discount")

    @api.onchange('price_unit')
    def auto_price(self):
        if self.price_unit and not self.price:
            self.price = self.product_id.lst_price

    @api.onchange('price', 'first_discount_percent', 'second_discount_percent')
    def auto_discount(self):
        self.price_unit = self.price

        if self.first_discount_percent:
            self.price_unit = self.price - (self.price * (self.first_discount_percent / 100))

        if self.second_discount_percent:
            self.price_unit = self.price_unit - (self.price_unit * (self.second_discount_percent / 100))

    @api.depends('taxes_id', 'price_unit')
    def compute_final_unit_cost(self):
        for line in self:
            line.final_unit_cost = line.price_unit
            taxes = sum(line.taxes_id.mapped('amount')) / 100

            if taxes:
                line.final_unit_cost += (line.price * taxes)

            if line.product_id.tracking != 'lot' and line.product_id.type != 'service':
                line.product_id.standard_price = line.final_unit_cost
