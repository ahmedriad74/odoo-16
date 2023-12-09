# -*- coding: utf-8 -*-

import base64
import xlrd 
from odoo import models, fields, _
import datetime


class UploadInvoicesWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    binary_file = fields.Binary(string='Sheet')


    def action_import(self):
        wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
        sheet = wb.sheets()[0]

        # all_products = self.env['product.template'].search([])
        lot = self.env['stock.production.lot']
        product_ids = dict()

        for row in range(1, sheet.nrows):
            
            product_id = int(sheet.cell_value(row,0))

            price = sheet.cell_value(row,1)
            default_code = sheet.cell_value(row,2)
            tuple_time = (xlrd.xldate_as_tuple(sheet.cell_value(row,3), wb.datemode))
            expiration_date = datetime.datetime(*tuple_time[0:3])

            if not product_ids.get(product_id):
                product_ids[product_id] = True

                temp = datetime.datetime(1899, 12, 30)
                delta = expiration_date - temp
                date_excel = int(float(delta.days) + (float(delta.seconds) / 86400))

                lot.create({
                    'product_id': product_id,
                    'company_id': self.env.company.id,
                    'expiration_date': expiration_date,
                    'name': '%s-%s'%(expiration_date.strftime("%d/%m/%Y"), default_code),
                    'py_barcode': '%s.%s'%(default_code, date_excel),
                    'py_price_unit': price
                })
        