from odoo import models, fields, api, _, SUPERUSER_ID

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def change_size_page(self, items):
        paper_format = self.env.ref('pyramids_internal_transfer_receipt.paperformat_portrait_internal')
        paper_format.with_user(SUPERUSER_ID).page_height = 90 + (len(items) * 20)
