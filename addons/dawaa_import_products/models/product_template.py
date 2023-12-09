# -*- coding: utf-8 -*-

from odoo import models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"


    def action_import_products(self):
    
        view = self.env.ref('dawaa_import_products.view_import_products_wizard')

        return {
            'name': _('Upload Invoices'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.products.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': dict(self.env.context),
        }
    