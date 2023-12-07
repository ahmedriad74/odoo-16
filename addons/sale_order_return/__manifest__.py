# -*- coding: utf-8 -*-
{
    'name': "Sale Order Return",

    'summary': """
        Return order from sale order""",

    'author': "Roaya",
    'website': "https://www.roayadm.com",

    'category': 'Sale',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sales_order_employee'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_order_return.xml'
    ],
}
