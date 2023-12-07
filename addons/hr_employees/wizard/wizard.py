# -*- coding: utf-8 -*-

import base64
import xlrd 
from odoo import models, fields, _
import datetime


class UploadWorkHrsSheetWizard(models.TransientModel):
    _name = 'upload.workhrs.sheet.wizard'
    _description = 'Upload Work Hours Sheet Wizard'

    binary_file = fields.Binary(string='Sheet')

    # def action_upload(self):
    #     wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
    #     sheet = wb.sheets()[0]

    #     EMPLOYEE = self.env['hr.employee']
    #     employee_codes = dict()

    #     for row in range(1, sheet.nrows):
    #         if sheet.cell_value(row,0):
    #             code = int(sheet.cell_value(row,0))
    #             empl_work_hrs = sheet.cell_value(row,5)
    #             employee_codes[code] = empl_work_hrs

    #     employee_records = EMPLOYEE.search([('barcode', 'in', list(employee_codes.keys()))])

    #     for employee in employee_records:
    #         employee.work_hrs = employee_codes.get(int(employee.barcode))
    
    def action_upload_data(self):
        wb = xlrd.open_workbook(file_contents = base64.decodebytes(self.binary_file))
        sheet = wb.sheets()[0]

        EMPLOYEE = self.env['hr.employee']
        employee_codes = dict()

        for row in range(1, sheet.nrows):
            if sheet.cell_value(row,3):
                empl_name = sheet.cell_value(row,0)
                code = int(sheet.cell_value(row,3))
                empl_hour_price = sheet.cell_value(row,4)
                empl_work_hrs = sheet.cell_value(row,5)
                employee_codes[code] = [empl_name, empl_hour_price, empl_work_hrs]

        employee_records = EMPLOYEE.search([('barcode', 'in', list(employee_codes.keys()))])

        for employee in employee_records:
            data_lst = employee_codes.get(int(employee.barcode))
            
            employee.name = data_lst[0]
            if data_lst[1]:
                employee.hour_price = data_lst[1]
            if data_lst[2]:
                employee.work_hrs = data_lst[2]
