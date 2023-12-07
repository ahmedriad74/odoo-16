import base64
from shutil import move
import xlrd 
from odoo import models, fields, _
from odoo.exceptions import UserError
from collections import defaultdict

class CreateTransfersWizard(models.TransientModel):
    _name = 'create.transfers.wizard'
    _description = 'Create Transfers Wizard'

    binary_file = fields.Binary(string='Sheet')

    def action_create_trans(self):
        wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
        sheet = wb.sheets()[0]

        all_products = self.env['product.template'].search([('default_code', '!=', False)])

        stock_move = self.env['stock.move']
        stock_picking = self.env['stock.picking']
        stock_picking_type = self.env['stock.picking.type']
        stock_location = self.env['stock.location']

        dic = defaultdict(list)
        destinations = {}
        picking_type = False

        location_id = stock_location.search([('complete_name', '=', 'WH/1Stock')]).id

        for product in all_products:
            dic[product.default_code].append([product.id, product.name, product.uom_id.id])

        data = defaultdict(list)

        for row in range(1, sheet.nrows):
            default_code = sheet.cell_value(row,0)

            if type(default_code) == float:
                default_code = str(int(default_code))

            values = {
                'default_code': default_code,
                'qty': int(sheet.cell_value(row,1)),
            }

            if destinations.get(sheet.cell_value(row,2)) == None:
                destinations[sheet.cell_value(row,2)] = stock_location.search([('complete_name', '=', sheet.cell_value(row,2))]).id
                picking_type = stock_picking_type.search([('code','=','internal'), ('default_location_dest_id','=', destinations[sheet.cell_value(row,2)])]).id

            data['{}_{}_{}'.format(sheet.cell_value(row,2), destinations[sheet.cell_value(row,2)], picking_type)].append(values)

        picking_default_values = stock_picking.default_get(stock_picking.fields_get())

        for key, values in data.items():
            lst_key = key.split('_')

            location_dest_id = int(lst_key[1])

            picking_type = int(lst_key[2])

            picking_fields = [dict(picking_default_values, **{
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': picking_type,
                'origin': 'Excel'})]

            picking_id = stock_picking.create(picking_fields).id

            picking_lines = []

            for value in values:
                if value['default_code'] in dic:
                    if(len(dic[value['default_code']]) == 1):
                        picking_lines.append({
                            'name': dic[value['default_code']][0][1],
                            'product_id': dic[value['default_code']][0][0],
                            'product_uom_qty': value['qty'],
                            'product_uom': dic[value['default_code']][0][2],
                            'py_quantity': value['qty'],
                            'picking_id': picking_id,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,

                        })

            stock_move.create(picking_lines)               
