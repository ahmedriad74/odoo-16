# -*- coding: utf-8 -*-
{
    'name': "Cash Back",

    'summary': """
        Create Customer Cash Back System
    """,

    'description': """
        Create Customer Cash Back System
    """,

    'author': "AMR SALAH",
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['sale', 'account', 'stock', 'product'],

    'data': [
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/pricelist.xml',
        'views/stock_picking.xml',
    ],
}
