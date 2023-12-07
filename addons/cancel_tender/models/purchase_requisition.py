from odoo import models, fields, api, _


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def action_cancel_tender(self):
        for pr in self:
            pr.state = 'cancel'