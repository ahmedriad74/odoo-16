# -*- coding: utf-8 -*-
{
    'name': "Sale Order Cash or Remit",

    'summary': """
        Select user payment type
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Extra Tools',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sale','account'],

    'data': [
        'views/account_move.xml',
        'views/pricelist.xml'
    ],
}