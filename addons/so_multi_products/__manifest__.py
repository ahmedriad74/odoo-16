{
    'name': 'SO Multi Product Selection',
    'summary': 'Sale order and Purchase order Multiple Product Selection',
    'description': """
        This module provide select multiple products
        Features includes managing
            * allow to choose multiple products at once in sale order
    """,
    'author': 'Roaya',
    'website': 'https://www.roayadm.com',
    'category': 'Sales',
    'version': '16.0.1.0.0',
    'license': 'OPL-1',
    'depends': ['product', 'sale_management','hr_expense','point_of_sale'],

    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
        'security/security.xml',
        'security/ir.model.access.csv'
    ]
}
