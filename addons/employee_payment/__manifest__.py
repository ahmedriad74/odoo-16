# -*- coding: utf-8 -*-
{
    'name': "Employee Payment",

    'summary': """
        Add employee on payment with pin&&amount read only
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Account',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['account','sales_order_employee'],

    'data': [
        'views/employee.xml',
        'views/payment.xml',
        'wizard/account_payment_register.xml',
        ],
}