# -*- coding: utf-8 -*-
{
    'name': "Sales Order Employee",

    'summary': """
        Add sales/delivery employee on sales order""",

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license': 'OPL-1',
    # upgrade16 ==> 'sale_coupon' -> 'sale_loyalty'
    'depends': ['hr', 'pyramids_auto_assign', 
                'set_shipping_cost', 'sale_loyalty', 
                'sales_team', 'stock', 'sales_report_auth'],

    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/sale_team.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/choose_delivery_carrier.xml',
        'wizard/delivery_wizard.xml',
        'wizard/avg_delivery_duration.xml'
    ],
}
