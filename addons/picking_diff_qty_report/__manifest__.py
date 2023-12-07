# -*- coding: utf-8 -*-
{
    'name': "Picking Diff. Qty Report",

    'summary': """
        Picking Diff. Qty Report""",

    'description': """
        Picking Diff. Qty Report
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['lot_management'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/templates.xml',
    ],
}
