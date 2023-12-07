# -*- coding: utf-8 -*-
{
    'name': "Pyramids Partner Fields",

    'summary': """
        Add new fields to partner""",

    'description': """
        Add new fields to product
        1-Gender
        2-House Number
        3-Floor Number
        4-Landmark
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Base',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['base'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
