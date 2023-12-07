# -*- coding: utf-8 -*-
{
    'name': "Stock Control",

    'summary': """
        - Mange Stock Operations
    """,

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Stock',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['consumption_rate','user_stock_control','replenishment_internal_transfer'],

    'data': [
        'security/ir.model.access.csv',
        'data/mail_channel.xml',
        'data/reorder_cron.xml',
        'views/stock_picking.xml',
        'views/stock_orderpoint.xml',
        'views/stock_backorder.xml',
        'views/stock_route.xml',
        'views/stock_move_views.xml',
        'views/stock_warehouse.xml',
        # 'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/stock_orderpoint.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'stock_control/static/src/js/stock_orderpoint_list_controller.js',
            'stock_control/static/src/js/stock_orderpoint_list_model.js'
        ]
    },
}
