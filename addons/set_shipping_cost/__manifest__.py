# -*- coding: utf-8 -*-
{
    'name': "Set Shipping Cost",

    'summary': """
        Set Shipping Cost""",

    'author': "Roaya",
    'website': "https://www.roayadm.com",
    'category': 'Sales',
    'version': '16.0',
    'license': 'OPL-1',
    'depends': ['delivery','pyramids_pricelist', 'sales_team', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'data/delivery_data.xml',
        'wizard/choose_delivery_carrier.xml'
        ],
}