# -*- coding: utf-8 -*-
{
    'name': "Lot Management",

    'summary': """
        -Sell/Buy From Lot
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '16.0',
    'depends': ['sale_stock', 'purchase_stock', 
                'product_expiry', 'pyramids_product_fields', 
                'pyramids_pricelist', 'sales_order_employee'],

    'data': [
        'views/templates.xml',
        'views/stock_picking.xml',
        'views/stock_production_lot.xml',
        'views/stock_quant.xml',
        'views/sale_order.xml',
        'views/product_category.xml',
        'views/cron_update_lot_price.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'lot_management/static/src/scss/sale_order.scss',
        ]
    }
}
