# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Kolyna Subscription Extension',
    'summary': 'Kolyna Subscription Extension',
    'author': 'Odoo IN',
    'description': """
        Kolyna Subscription Extension
    """,
    'category': 'Accounts',
    'depends': [
        'sale_management',
        'sale_subscription'
    ],
    'data': [
        'views/subscription.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
