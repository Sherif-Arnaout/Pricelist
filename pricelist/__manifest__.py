{
    'name': 'Product Pricelist',
    'version': '17.0.0.1',
    'summary': 'Easily share and print product prices with your customers without the need to create a quotation',
    'description': 'Advanced Pricelist',
    'category': 'Sales',
    'author': 'Sherif Arnaout',
    'license': 'AGPL-3',
    'depends': ['base',
                'product',
                'sale',
                'report_xlsx',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/pricelist.xml',
        'views/action_report_pricelist.xml',
        'reports/report_pricelist.xml',
        'reports/report_pricelist_document.xml',
        'wizards/pricelist_report_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pricelist/static/src/css/pricelist.css',
        ],
    },
    'images': [
        'static/description/main_screenshot.png',  
    ],
    'demo': ['Demo'],
    'application': True,
    'installable': True,
    'auto_install': False,
    "price": "10",
    "currency": "EUR"
}
