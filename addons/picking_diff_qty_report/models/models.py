# -*- coding: utf-8 -*-

from odoo import models
from io import BytesIO
import xlsxwriter
import base64

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def export_pciking_diff(self):
        files_to_create = []
        attachments = self.env['ir.attachment']
        wizard = self.env['wizard.report.excel']

        for picking in self.browse(self._context.get('active_ids', [])):
            file = BytesIO()
            workbook = xlsxwriter.Workbook(file)
            worksheet = workbook.add_worksheet(picking.name)

            move_lines = picking.move_ids_without_package.sorted(lambda x:x.product_id.name)
            has_serial_number = any(move_line.lot_id or move_line.lot_name for move_line in picking.move_line_ids)

            user = 'Partner'
            headers = ['Reference', user, 'Phone', 'Tax ID', 'Order', 'Status','Scheduled Date','From', 'To']
            header_format = workbook.add_format({'bold': True, 'align': 'center'})
            data_format = workbook.add_format({'align': 'center'})

            data = [
                picking.name,
                picking.partner_id.name or '-',
                picking.partner_id.phone or '-',
                picking.sudo().partner_id.vat or '-',
                picking.origin or '-',
                picking.state or '-',
                picking.scheduled_date,
                picking.location_id.display_name or '-',
                picking.location_dest_id.display_name or '-',
            ]
    
            if picking.picking_type_id.code=='outgoing' and picking.partner_id:
                user = 'Customer'
            elif picking.picking_type_id.code=='incoming' and picking.partner_id:
                user = 'Vendor'
            elif picking.picking_type_id.code=='internal' and picking.partner_id:
                user = 'Warehouse'

            for col in range(9):
                worksheet.set_column(0, col, 20)
                worksheet.write(0, col, headers[col], header_format)

                if headers[col] == 'Scheduled Date':
                    date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'center'})
                    worksheet.write(1, col, data[col], date_format)
                else:
                    worksheet.write(1, col, data[col], data_format)

            last_row = 0

            if picking.move_line_ids and picking.move_ids_without_package:
                worksheet.write(4, 0, 'Move Lines', header_format)
                move_line_headers = [
                    'Code',
                    'Product',
                    'Description',
                    'Demand',
                    'Uom' if self.env.user.has_group('uom.group_uom') else None,
                    'Reserverd',
                    'Uom' if self.env.user.has_group('uom.group_uom') else None,
                    'Diff' if has_serial_number else None,
                ]

                for col in range(8):
                    worksheet.write(5, col, move_line_headers[col], header_format)

                last_row = 6

                for move in move_lines:
                    if (move.product_uom_qty - move.quantity_done) != 0:
                        worksheet.write(last_row, 0, move.product_id.default_code, data_format)
                        worksheet.write(last_row, 1, move.product_id.name, data_format)
                        worksheet.write(last_row, 2, move.product_id.description_picking or '-', data_format)
                        worksheet.write(last_row, 3, move.product_uom_qty)
                        worksheet.write(last_row, 4, move.product_uom_id if self.env.user.has_group('uom.group_uom') else None, data_format)
                        worksheet.write(last_row, 5, move.quantity_done, data_format)
                        worksheet.write(last_row, 6, move.product_uom_id if self.env.user.has_group('uom.group_uom') else None, data_format)
                        worksheet.write(last_row, 7, move.product_uom_qty - move.quantity_done, data_format)

                        last_row += 1

            worksheet.write(last_row+4, 0, picking.bag or 0, data_format)
            worksheet.write(last_row+4, 1, 'شنطة', header_format)

            worksheet.write(last_row+5, 0, picking.box or 0, data_format)
            worksheet.write(last_row+5, 1, 'كرتونة', header_format)

            worksheet.write(last_row+6, 0, picking.fridge or 0, data_format)
            worksheet.write(last_row+6, 1, 'ثلاجة', header_format)

            workbook.close()

            files_to_create.append({
                'name': picking.name,
                'datas': base64.encodebytes(file.getvalue()),
            })

        # create excel files 
        attachment_ids = attachments.create(files_to_create)
        # create wizard with excel files
        wizard_id = wizard.create({
            'attachment_ids': attachment_ids.ids
        })

        return {
            'name': ('Reports'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wizard_id.id,
            'res_model': 'wizard.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }        
