# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LocationTransferWizard(models.Model):
    _inherit = 'stock.location'
    _description = 'Print Product Transfer Wizard'

    mrm_location_stock_id = fields.Many2one('print.transfer.wizard')


class TransferWizard(models.Model):
    _name = 'print.transfer.wizard'
    _description = 'Print Product Transfer Wizard'

    stock_from_ids = fields.One2many('stock.location', 'mrm_location_stock_id', string="Stock", required=True,
                                     domain="[('usage', '=', 'internal')]")
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)

    def action_print_transfer(self):
        if not self.date_to or not self.date_from:
            raise UserError(_("Form and To Date is missing, this report cannot be printed."))
        if not self.stock_from_ids or len(self.stock_from_ids) == 0:
            raise UserError(_("Stock is missing, this report cannot be printed."))
        if not self.env.user.property_warehouse_id.lot_stock_id.id:
            raise UserError(_("User Warehouse is missing, this report cannot be printed."))

        data = {
            'form_data': self.read()[0],
            'my_location_warehouse': self.env.user.property_warehouse_id.lot_stock_id.id
        }
        return self.env.ref('print_product_transfer_report.action_report_transfer_report').report_action(self, data=data)

