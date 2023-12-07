# -*- coding: utf-8 -*-
{
    'name': "dawaa_import_products",
    'summary': """
        Import Products Excel Sheet
    """,
    'description': """
        Import Products Excel Sheet
    """,
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['base', 'stock', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/view.xml',
    ],
}
