# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime
from collections import defaultdict
import xlsxwriter
import base64
from io import BytesIO

class AvgDeliveryDurationReport(models.TransientModel):
    _name = 'avg.delivery.duration.report'
    _description = 'Avg Delivery Duration Report'

    branch_ids = fields.Many2many('crm.team', string='Team')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    attachment_id = fields.Binary()

    def get_total_secs(self, time_list):
        total_seconds = 0

        if len(time_list) > 1:
            days = time_list[0]
            days_to_seconds = int(days) * 86400
            time = datetime.strptime(time_list[1], '%H:%M:%S')
            total_seconds += days_to_seconds
        else:
            time = datetime.strptime(time_list[0], '%H:%M:%S').time()

        hrs_to_secs = int(time.strftime('%H')) * 3600
        mins_to_secs = int(time.strftime('%M')) * 60
        secs = int(time.strftime('%S'))
        total_seconds += hrs_to_secs
        total_seconds += mins_to_secs
        total_seconds += secs

        return total_seconds

    def get_data(self):
        data_dict = defaultdict(list)
        data_lst = self.env['sale.order'].search_read([
                                            ('state', 'not in', ('draft', 'cancel')),
                                            ('delivery_employee_id', '!=', False),
                                            ('team_id', 'in', self.branch_ids.ids),
                                            ('date_order', '>=', self.date_from), 
                                            ('date_order', '<=', self.date_to)], 
                                            ['delivery_employee_id', 'delivery_duration'], order='delivery_employee_id')
        
        for data in data_lst:
            employee = data.get('delivery_employee_id')
            duration = data.get('delivery_duration').split() or 0

            if duration:
                total_seconds = self.get_total_secs(duration)
                data_dict[employee].append(total_seconds) 

        return data_dict

    def action_print_report(self):
        file = BytesIO()
        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet('Delivery Duration Report')
        headers = ['Delivery Employee', 'Avg Duration']
        header_format = workbook.add_format({'bold': True, 'align': 'center'})
        data_format = workbook.add_format({'align': 'center'})
        row = 1

        for col in range(2):
            worksheet.set_column(0, col, 20)
            worksheet.write(0, col, headers[col], header_format)

        data = self.get_data()

        for employee in data:
            secs_lst = data[employee]
            total_seconds = sum(secs_lst)
            total_orders = len(secs_lst)
            avg_seconds = total_seconds / total_orders

            days = divmod(avg_seconds, 86400)
            hours = divmod(days[1], 3600)
            minutes = divmod(hours[1], 60)
            seconds = divmod(minutes[1], 1)

            if days[0] == 0:
                avg_duration = "%d:%d:%d" % (
                    hours[0], minutes[0], seconds[0])
            else:
                avg_duration = "%d %d:%d:%d" % (
                    days[0], hours[0], minutes[0], seconds[0])
        
            worksheet.write(row, 0, employee[1], data_format)
            worksheet.write(row, 1, avg_duration, data_format)

            row += 1

        workbook.close()

        self.write({
            'attachment_id': base64.encodebytes(file.getvalue()),
            })

        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=avg.delivery.duration.report&id=" + str(self.id) + "&field=attachment_id&download=true&name=avg_delivery_duration.xlsx",
            'target': 'self'
        }
        return action
