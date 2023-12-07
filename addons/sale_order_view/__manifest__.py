# -*- coding: utf-8 -*-
{
    'name': "Sale Order View",

    'summary': """
        Remove QU expiration date and optional product tab and payment term
        Also add domain on customer only
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license':"OPL-1",
    'depends': ['sale','delivery','sales_team'],

    'data': [
        'security/security.xml',
        'views/views.xml',
    ]
}
