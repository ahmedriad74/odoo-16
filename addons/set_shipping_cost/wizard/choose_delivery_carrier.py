# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError

class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = "choose.delivery.carrier"
    
    price = fields.Float('Price')
    
    @api.onchange('price')
    def _onchange_price(self):
        carrier_id = self.env.ref('set_shipping_cost.fixed_delivery_carrier')

        if not self.carrier_id:
            self.price = 7
            carrier_id.with_user(SUPERUSER_ID).write({'fixed_price':7})

        if self.price > 0:
            carrier_id.with_user(SUPERUSER_ID).write({'fixed_price':self.price})

        if self.price < 7: 
            carrier_id.with_user(SUPERUSER_ID).write({'fixed_price':7})

        self.carrier_id = carrier_id  
          
        # on change carrier_id
        self.delivery_message = False
        if self.carrier_id.delivery_type in ('fixed', 'base_on_rule'):
            vals = self._get_shipment_rate()
            if vals.get('error_message'):
                return {'error': vals['error_message']}
        else:
            self.display_price = 0
            self.delivery_price = 0
            
    
    
