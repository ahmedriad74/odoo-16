{
    'name': 'Send & Receive Request',
    'version': '13.0',
    'author': 'Roaya',
    'license': 'AGPL-3',
    'website': 'https://www.roayadm.com',
    'category': 'Accounting',
    'summary': 'Send & Receive Request',
    'depends': ['account','sale', 'mandatory_analytical_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'views/payment_statement_report.xml'
    ],
    'installable': True,
}
