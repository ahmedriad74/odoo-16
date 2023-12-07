# -*- coding: utf-8 -*-
{
    'name': "Pyramids Own Invoice",

    'summary': """
        Own sales only invoice of today
    """,
    
    'description':"""
        Own sales only sales of today
        1-change menu ow sequence
        2-make all menu under advisor
    """,
        
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license': "OPL-1",
    'depends': ['account','sales_order_employee','sale_order_cash_remit'],

    'data': [
        'views/views.xml',
    ],
}