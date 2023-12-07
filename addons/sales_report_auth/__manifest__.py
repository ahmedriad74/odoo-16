# -*- coding: utf-8 -*-
{
    'name': "Sales Report Auth",
    'summary': """Add specific employee that can access sales report""",
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sale_enterprise'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/views.xml'
    ],
}
