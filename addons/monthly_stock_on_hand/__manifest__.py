# -*- coding: utf-8 -*-
{
    'name': "Dawaa Stock on Hand",

    'summary': """
        Comapre stock quantities and value between months 
    """,

    'description': """
        Comapre stock quantities and value between months 
    """,

    'author': "AMR SALAH",
    'category': 'Inventory',
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['stock', 'dawaa_product_fields'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
