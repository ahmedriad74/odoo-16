# -*- coding: utf-8 -*-
{
    'name': "Replenishment to internal transfer ",

    'summary': """
        Replenishment to Internal Transfer""",

    'description': """
        Replenishment to internal transfer Make current user the partner & assign schedule to other user to validate
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Stock',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['pyramids_auto_assign'],

    'data': [
        'views/views.xml',
        'security/picking_security.xml'
    ],
}
