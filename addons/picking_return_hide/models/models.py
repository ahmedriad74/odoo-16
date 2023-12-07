# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    show_return = fields.Boolean(compute='_compute_status')
    
    @api.depends('partner_id')
    def _compute_status(self):
        for rec in self:
            rec.show_return = True
            Flag = True

            if rec.state not in ('done') :
                Flag = False
            elif rec.state in ('done') :
                if rec.picking_type_id and rec.picking_type_id.code == 'outgoing' and rec.sale_id:
                    if len(rec.sale_id.invoice_ids):
                        last_inv = rec.sale_id.invoice_ids.sorted(lambda x:x.id)[-1]
                        if last_inv.move_type == 'out_invoice' and last_inv.payment_state not in ('paid', 'in_payment'):
                            Flag = False    

            rec.show_return = Flag
            
                                  
