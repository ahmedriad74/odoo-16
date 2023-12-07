# -*- coding: utf-8 -*-
{
    'name': "Consumption Rate",
    'summary': """
        Add Consumption Rate to Reordering Rule""",
    'description': """
        add consumption rate to reordering rule
        -add user to purchase group and remove menu
        -stock.warehouse.orderpoint add inventory user write/create
        -purchase.requisition add inventory user write/create
    """,    
    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Inventory',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['sale_stock','lot_management',
                'dawaa_product_fields', 'show_inv_reporting_for_sales', 
                'purchase_requisition', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_security.xml',
        'data/ir_sequence_data.xml',
        'views/stock_warehouse.xml',
        'views/stock_location.xml',
        'views/consumption_rate.xml',
        'views/orderpoint.xml',
        'wizard/stock_reorder_setting.xml'
    ],
}
