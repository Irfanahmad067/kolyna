# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kolyna Form Theme',
    'version': '15.0.0.1',
    'author': "Dootix",
    'website': "https://www.dootix.com",
    'category': 'Extra Tools',
    'summary': 'Kolyna Form Theme',
    'depends': [
        'dootix_partner',
        'contacts',
        'website',
        'kolyna_sale',
        'mail',
    ],
    'data': [
        "views/kolyna_form_template.xml",
        'data/mail_template.xml',
    ],
    'auto_install': True,
    'installable': True,
    'assets': {
        'web.assets_frontend': [
            'kolyna_theme/static/src/js/kolyna_theme.js',
            'kolyna_theme/static/src/js/fr-ch.js',
            'kolyna_theme/static/src/scss/kolyna_theme.scss',
        ],
    }
}
