# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cash Difference',
    'summary': """
        Add less than 2 pound to difference cash and max 2 pound
    """,
        
    'category': 'Account',
    'depends' : ['bank_payment_journal'],
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'license': 'OPL-1',
    'version' : '16.0',
    'data': [
        'views/account_journal.xml'
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
