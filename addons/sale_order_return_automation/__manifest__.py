# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Order Return Automation',
    'author':'Roaya',
    'category': 'Sales',
    'summary': """Enable auto sale workflow with return sale order. Include operations like Auto Create Invoice, Auto Validate Invoice and Auto Transfer Delivery Order.""",
    'website': 'https://www.roayadm.com/',
    'version' : '16.0',
    'license': 'OPL-1',
    'depends' : ['sale','stock'],
    'data': [
        'views/stock_warehouse.xml',
    ],

}
