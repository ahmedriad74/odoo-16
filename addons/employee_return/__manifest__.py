# -*- coding: utf-8 -*-
{
    'name': "Employee Return",

    'summary': """
        -Add employee on retrun with pin read only 
        -Can't resturn items after 14 days
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Stock',
    'version': '16.0',
    'license': "OPL-1",
    'depends': ['sales_order_employee','sales_report_auth'],

    'data': [
        'views/stock_picking.xml',
        'views/employee.xml',
        'wizard/stock_picking_return_views.xml'
        ],
}
