# -*- coding: utf-8 -*-

import base64
import xlrd 
from odoo import models, fields, _
from odoo.exceptions import UserError

class UploadInvoicesWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    binary_file = fields.Binary(string='Sheet')


    def action_import(self):
        wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
        sheets = wb.sheets()
        sheet_no = 0

        levelf_id = self.env['product.levelf'].search([('ro_target', '=', True)])

        if levelf_id:
            products_ir = set()
            products_name = set()

            all_products = self.env['product.template'].search([])

            for sheet in sheets:
                if sheet_no > 0:
                    for row in range(0, sheet.nrows):
                        cell_value = sheet.cell_value(row,0).split(']')
                        ir = cell_value[0].strip()
                        name = cell_value[1].strip()

                        products_ir.add(ir[1:])
                        products_name.add(name)
                else:
                    for row in range(1, sheet.nrows):
                        products_ir.add(sheet.cell_value(row,0))
                        products_name.add(sheet.cell_value(row,1))

                sheet_no += 1

            for product in all_products:
                if (product.name in products_name) and (product.default_code in products_ir):
                    product.levelf_id = levelf_id.id

        else:
            raise UserError(_("Please check target in levelf 'App'."))
