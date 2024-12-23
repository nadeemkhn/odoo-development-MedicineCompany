{
    'name': ' medicine company',
    'version': '1.2',
    'summary': 'medicine company ',
    'sequence': -100,
    'author': 'Nadeemkhan',
    'description': """ medicine company  """,
    'category': 'Productivity',
    'website': 'https://www.odoo.com/app/invoicing',
    'assets': {
        'web.assets_backend': [
            'My_company/static/src/css/custom_style.css',
        ],
    },
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_seq.xml',
        'data/purchase_seq.xml',
        'data/medicine_seq.xml',
        'data/stock.delivery.xml',
        'views/main_menu.xml',
        'views/medicine.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/customer.xml',
        'views/stock_delivery.xml',
        'views/distributor.xml',
        'views/supply.xml',
        'report/reports_action.xml',
        'report/report_sale_order.xml',
        'report/report_purchase_order.xml',
        'report/medicine_reports.xml',
    ],
    'installable': True,
    'application': True,
    'auto_Install': False,
}
