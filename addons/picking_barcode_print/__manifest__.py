# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Barcode From Picking',
    'summary': """
        Barcode field in Picking order line and print""",
        
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Extra Tools',
    'version' : '16.0',
    'license': 'OPL-1',
    'depends' : ['lot_management'],

    'data': [
        'reports/barcode.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
