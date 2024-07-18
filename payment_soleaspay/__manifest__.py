{
    'name': 'Odoo - Soleaspay Payment Gateway Integration',
    'category': 'Accounting',
    'summary': 'Odoo  Soleaspay Payment ecommerce integration',
    'version': '15.0.1.0.0',
    'description': """Odoo Soleaspay Payment gateway""",
    'depends': [
        'payment',
        'website_sale'
    ],
    'author': 'MYSOLEAS',
    'website': 'https://www.mysoleas.com/',
    'data': [
        "views/soleaspay_payment_view.xml",
        "views/soleaspay_payment_templates.xml",
        "data/payment_acquirer_data.xml",
    ],
    'images': [],
    'installable': True,
    'license': 'LGPL-3',
}
