# -*- coding: utf-8 -*-
{
    'name': "Auto Assign",

    'summary': """
        auto assign sale team to analytic account/warehouse
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sale','account','stock','analytic','sales_team','sale_stock','purchase'],

    'data': [
        'views/analytic_accounts.xml',
        # upgdrade16
        'views/account_analytic_dist_model.xml',
        # 
        'views/warehouses.xml',
        'views/account_journal.xml',
        'views/invoice_payment.xml'
        ],
}