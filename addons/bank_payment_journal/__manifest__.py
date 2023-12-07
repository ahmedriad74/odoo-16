# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Bank Charges',
    'summary': """
        Add bank charges""",
        
    'category': 'Account',
    'depends' : ['account'],
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'version' : '16.0',
    'license':'OPL-1',
    'data': [
        'views/account_journal.xml',
        'views/account_payment.xml',
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
