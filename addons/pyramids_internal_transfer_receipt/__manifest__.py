# -*- coding: utf-8 -*-
{
    'name': "Internal Transfer Receipt",

    'summary': """
        Receipt for internal transfer""",

    'author': "Roaya",
    'website': "https://www.roayadm.com",

    'category': 'Inventory',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sales_order_employee', 
                'replenishment_internal_transfer', 
                'report_pdf_options'],

    'data': [
        'views/receipt_report.xml',
    ],
}
