# -*- coding: utf-8 -*-
{
    'name': "Print Product Transfer Report",

    'summary': """
        Print all Transfer happened on Product 
        """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Purchase',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['stock', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/print_transfer.xml',
        'reports/report.xml',
    ],
}
