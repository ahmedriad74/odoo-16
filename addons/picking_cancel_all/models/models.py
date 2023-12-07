# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def mass_cancel(self):
        self = self - self.filtered(lambda pick: pick.state in ['validate2','done','cancel'])
        for picking in self:
            picking.action_cancel()


