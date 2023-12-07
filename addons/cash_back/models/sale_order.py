# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_cash_back_amount = fields.Float(related='partner_id.cash_back_amount')
    customer_got_offer = fields.Boolean(related='partner_id.got_offer')

    @api.onchange('pricelist_id')
    def onchange_price_list(self):
        for record in self:
            cash_back_pricelist = record.pricelist_id.campaign == 'cash_back'

            if cash_back_pricelist and self.partner_id.name:
                if self.partner_id.name == ' ' or\
                    'walk' in self.partner_id.name.lower():
                    raise ValidationError(_("This customer is not allowed to get offer"))

            elif cash_back_pricelist and self.customer_got_offer:
                raise ValidationError(_("This customer already got cash back offer in order '%s'.") %self.partner_id.cash_back_order)

    def action_confirm(self):
        cash_back_amount = 0

        # first time buy
        if self.pricelist_id.campaign == 'cash_back':
            pl_items = self.pricelist_id.item_ids
            
            for line in self.order_line:
                if line.product_id.categ_id in pl_items.mapped('categ_id'):
                    cash_back_amount += line.price_subtotal
                    
            # applied conditions
            if cash_back_amount >= 500 and cash_back_amount < 750:
                self.partner_id.cash_back_amount = cash_back_amount * .1
            elif cash_back_amount >= 750 and cash_back_amount <= 1500:
                self.partner_id.cash_back_amount = cash_back_amount * .15
            elif cash_back_amount > 1500:
                self.partner_id.cash_back_amount = cash_back_amount * .2
                
            self.partner_id.got_offer = True
            self.partner_id.cash_back_order = self.name

        # second time buy
        elif self.partner_id.got_offer and self.partner_id.cash_back_amount > 0:
            self.partner_id.got_offer = False
            reward_product = self.env['product.pricelist'].search([('campaign', '=', 'cash_back')]).reward_product

            if self.amount_total >= self.customer_cash_back_amount:
                self.order_line.create({
                    'name': reward_product.name,
                    'product_id': reward_product.id,
                    'price_unit': self.customer_cash_back_amount * -1,
                    'product_uom_qty': 1,
                    'order_id': self.id,
                })
                self.partner_id.cash_back_amount = 0

            elif self.amount_total < self.customer_cash_back_amount:
                rest_money = self.customer_cash_back_amount - self.amount_total

                self.order_line.create({
                    'name': reward_product.name,
                    'product_id': reward_product.id,
                    'price_unit': self.amount_total * -1,
                    'product_uom_qty': 1,
                    'order_id': self.id,
                })
                self.partner_id.cash_back_amount = rest_money

        return super(SaleOrder, self).action_confirm()

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()

        res['hide_credit_note_btn'] = True if self.pricelist_id.campaign == 'cash_back' else False

        return res