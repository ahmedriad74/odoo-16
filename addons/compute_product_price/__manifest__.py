# -*- coding: utf-8 -*-
{
    'name': "Compute Product Price",

    'summary': """
        Compute Product Price
    """,

    'description': """
        Compute Product Price
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['product', 'stock', 'sales_team', 'account', 'purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml'
    ]
}
