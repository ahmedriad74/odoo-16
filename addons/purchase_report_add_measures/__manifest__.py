# -*- coding: utf-8 -*-
{
    'name': "Purchase Report Add Measures",

    'summary': """
        Purchase report Add Measures ( Source document)""",


    'author': "Roaya",
    'website': "http://www.roayadm.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '16.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','dawaa_product_fields'],

    # always loaded
    'data': [
        'views/purchase_report_views.xml'
    ],

}