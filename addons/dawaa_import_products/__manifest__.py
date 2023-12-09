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
    'version': '14.0',
    'depends': ['base', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/view.xml',
    ],
}
