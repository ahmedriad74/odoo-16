# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    hidden_location = fields.Boolean(related='location_id.hide_location')


    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        action = super(StockQuant, self)._get_quants_action(domain, extend)

        if not self.env.user.has_group('dawaa_hide_wh_locations.show_wh_locations'):
            if action.get('domain'):
                action['domain'] += [('hidden_location', '=', False)]
            # else:
            #     action['domain'] = [('hidden_location', '=', False)]

        return action