# -*- coding: utf-8 -*-
{
    'name': "Inventory",

    'summary': """
        This module is an extension of the module Inventory already existing in odoo but including
        more fields and features for products""",

    'description': """
        This modules allows you to be give specific and detail information for each product you store 
        in the pharmacy inventory and you are able to keep track of product entrying the stock and product
        leaving the stock through detailled report you can print for each product  or for all the products saved in this module. 
    """,

    'author': "Ange Taffo",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product.xml', 
        'reports/stock_report.xml',
        'reports/stock_template.xml',
        'reports/stock_entrees.xml',
        'views/menu.xml',
        'views/classe.xml',
        'views/dci.xml',
        'data/product_catg.xml',
        'data/family.xml',
        'data/dci_data.xml',
        'data/atc_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
