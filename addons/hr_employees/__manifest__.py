# -*- coding: utf-8 -*-
{
    'name': "Hr Employee Changes",

    'summary': """
        Make Changes to Hr Employee
    """,

    'description': """
        Make Changes to Hr Employee
    """,

    'author': "AMR SALAH",
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['base', 'hr', 'om_hr_payroll'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/views.xml',
    ],
}
