# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError
import requests
import uuid 

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sms_code = fields.Char('SMS Code')
    sent_sms_code = fields.Char()
    sms_phone_number = fields.Char('SMS Phone')
    sms_is_sent = fields.Boolean(default=False)
    is_sms_order = fields.Boolean(related='pricelist_id.is_sms_pl')

    def send_sms(self):
        new_code = str(uuid.uuid4())[:6]
        url = 'https://smssmartegypt.com/sms/api/json/'
        data = {'username': 'passant.ebrahim@aldawaapharmacies.com', 
                'password': '208E77*mT', 
                'sendername': 'Aldawaa ph', 
                'mobiles': self.phone or self.sms_phone_number, 
                'message': f'Dear customer your promo code is {new_code}'
            }
        
        response = requests.post(url, json=data).json()

        if type(response) == list and response[0].get('type') == 'success':
            self.sent_sms_code = new_code
            self.sms_is_sent = True
        elif response.get('error'):
            error_msg = response.get('error').get('msg')
            raise ValidationError(f'{error_msg}')

    def action_confirm(self):
        if self.pricelist_id.is_sms_pl and not self.sms_code:
            raise ValidationError('You have to provide sms code')
        if self.sms_code != self.sent_sms_code:
            raise ValidationError('Please check the code')

        return super().action_confirm()

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_sms_pl = fields.Boolean('SMS')
