# -*- coding: utf-8 -*-
{
    'name': "Account Move View",

    'summary': """
        Remove all unnecessary UI from Form View
    """,

    'description': """
        - Remove all unnecessary UI from Form View
        - Add group advisor to share action
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Accounting',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['consumption_rate', 'hide_sale_price'],

    'data': [
        'views/views.xml',
    ],
    'qweb': [
        "static/src/xml/account_payment.xml"
    ],
}
