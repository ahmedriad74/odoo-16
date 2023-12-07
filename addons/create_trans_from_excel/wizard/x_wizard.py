# -*- coding: utf-8 -*-

import base64
import xlrd 
from odoo import models, fields, _
from collections import defaultdict


class CreateTransfersWizard(models.TransientModel):
    _name = 'create.transfers.wizard'
    _description = 'Create Transfers Wizard'

    binary_file = fields.Binary(string='Sheet')


    def action_create_trans(self):
        wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
        sheet = wb.sheets()[0]

        stock_move = self.env['stock.move']
        stock_move_line = self.env['stock.move.line']
        stock_picking = self.env['stock.picking']
        stock_picking_type = self.env['stock.picking.type']
        stock_location = self.env['stock.location']

        location_id = sheet.cell_value(1,2)
        location_dest_id = stock_location.search([('complete_name', '=', 'WH/1Stock')]).id

        picking_type = stock_picking_type.search([('code','=','internal'), ('default_location_dest_id','=', location_dest_id)])

        picking_default_values = stock_picking.default_get(stock_picking.fields_get())

        picking_fields = [dict(picking_default_values, **{
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_type_id': picking_type.id,
            'origin': 'Excel'})]

        print(picking_fields)
        print(ds)
        picking_id = stock_picking.sudo().create(picking_fields).id

        data = defaultdict(list)

        for row in range(1, sheet.nrows):
            values = {
                'lot_id': sheet.cell_value(row,3),
                'qty_done': sheet.cell_value(row,4)
            }
            data[int(sheet.cell_value(row,0))].append(values)

        
        for key, items in data.items():
            move_line_qty = 0

            for lot in items:
                move_line_qty += lot['qty_done']

            move_id = stock_move.sudo().create({
                'name': sheet.cell_value(row,1),
                'product_id': key,
                'product_uom_qty': move_line_qty,
                'py_quantity': move_line_qty,
                'product_uom': int(sheet.cell_value(row,5)),
                'picking_id': picking_id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            }).id

            for lot in items:
                stock_move_line.sudo().create({
                'move_id': move_id,
                'lot_id': lot['lot_id'],
                'qty_done': lot['qty_done'],
                'product_id': key,
                'product_uom_id': int(sheet.cell_value(row,5)),
                'location_id': location_id,
                'location_dest_id': location_dest_id,
              })

          
        

