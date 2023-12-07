# -*- coding: utf-8 -*-

import time
from odoo import api, models, _


class ReportProductTransferXLS(models.AbstractModel):
    _name = 'report.print_product_transfer_report.transfer_xlsx'
    _description = 'Report Product Transfer XLS '
    _inherit = 'report.report_xlsx.abstract'

    def collect_data(self, data):
        form_data = data['form_data']
        if len(form_data['stock_from_ids']) == 1:
            location_ids = f"({form_data['stock_from_ids'][0]})"
        else:
            location_ids = tuple(form_data['stock_from_ids'])
        self._cr.execute("""
                    SELECT pt_cost.id, pt_cost.name, pt_qty.location_id, pt_cost.value_float , pt_qty.pp_qty
                    FROM(
                        -- count
                        SELECT count(qty_done) as pp_qty, product_id, location_id
                        FROM stock_move_line
                        WHERE
                            state = 'done' AND
                            date between '{}' AND  '{}' AND
                            location_id in {} AND
                            location_dest_id = {}
        		        GROUP BY product_id, location_id
        	        ) as pt_qty
        	        left join(
        	            -- 	get cost
        	            select pt.id,pt.name,irp_cost.value_float
        	            from product_template as pt
        	            left join(
                            select *
                            from (
                                select row_number() over(partition by irp.res_id, irp.company_id
                                order by
                                    irp.create_date desc)
                                    as RowNums,
                                    irp.create_date,
                                    irp.value_float,
                                    irp.name,
                                    irp.company_id ,
                                    irp.res_id
                                from
                                    ir_property irp
                                where
                                    irp.name = 'standard_price'
                            ) t3_irp
                        )as irp_cost
                        on irp_cost.res_id = concat('product.product,', pt.id)
        	        ) as pt_cost
        	        on pt_qty.product_id = pt_cost.id
        	        
        	        order by pt_cost.id

                """.format(form_data['date_from'], form_data['date_to'], location_ids,
                           data['my_location_warehouse']))
        products = self._cr.fetchall()
        return products

    def get_stock_name(self, id):
        return self.env['stock.location'].browse(id).complete_name

    def generate_xlsx_report(self, workbook, data, partners):
        products = self.collect_data(data)
        form_data = data['form_data']

        # style
        bold = workbook.add_format({'bold': True})
        boldCenter = workbook.add_format({'bold': True, 'align': 'center'})
        header = workbook.add_format({'bold': True, 'font_size': 15, 'align': 'center'})
        currency_acc = workbook.add_format({'num_format': '#,##0.00'})
        # End Style

        name = 'Product Transfer To  ' + self.get_stock_name(data['my_location_warehouse'])

        sheet = workbook.add_worksheet(name)
        sheet.set_column(0, 0, 45)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 8, 15)

        # Header
        # 1st row
        sheet.merge_range('A1:E1', name, header)
        # 2nd row
        sheet.write('B2', 'Date from:', bold)
        sheet.write('B3', form_data['date_from'])
        sheet.write('C2', 'Date to :', bold)
        sheet.write('C3', form_data['date_to'])
        # 3nd row
        # 4nd row
        # sheet.write('A5', 'ID', boldCenter)
        sheet.write('A5', 'Product', boldCenter)
        sheet.write('B5', 'Stock', boldCenter)
        sheet.write('C5', 'Count', boldCenter)
        sheet.write('D5', 'Cost Per Unit', boldCenter)
        sheet.write('E5', 'Total Cost', boldCenter)

        #
        # 5nd row
        row = 6
        for obj in products:
            # sheet.write(row, 0, obj[0]) # id
            sheet.write(row, 0, obj[1])
            sheet.write(row, 1, self.get_stock_name(obj[2]))
            sheet.write(row, 2, obj[4])  # count
            sheet.write(row, 3, obj[3], currency_acc)  # cost
            sheet.write(row, 4, obj[4] * obj[3], currency_acc)  # total cost

            row += 1
