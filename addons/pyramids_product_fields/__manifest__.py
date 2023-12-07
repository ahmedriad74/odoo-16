# -*- coding: utf-8 -*-
{
    'name': "Pyramids Product Fields",

    'summary': """
        Add new fields to product && order""",

    'description': """
        Add new fields to product
        1-availability -->available & shortage
        2-origin-->local & imported
        3-location-->refrigerator  & shelf
        4-status-->seasonal & urgent & pushed & normal
        &&
        order products
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/product_template_security.xml',
        'views/product_contract.xml',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
