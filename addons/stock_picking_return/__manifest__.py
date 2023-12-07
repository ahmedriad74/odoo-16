# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Return",

    'summary': """
        Make Return can select uom
        """,

    'description': """
        Make Return can select uom
        -Add inventory user to stock.valuation.layer model
        """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Inventory',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sale_stock'],

    'data': [
        'wizard/stock_picking_return.xml'
    ],
}