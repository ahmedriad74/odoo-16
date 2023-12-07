# -*- coding: utf-8 -*-
{
    'name': "Dawaa Product Fields",

    'summary': """
        add new fields to product (brand etc.)""",

    'description': """
        add new fields to product (brand etc.)
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Stock',
    'version': '16.1',
    'license': 'OPL-1',
    'depends': ['sale','base','contacts', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}