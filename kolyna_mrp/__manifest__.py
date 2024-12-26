# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kolyna MRP production scheduler',
    'category': 'Manufacturing',
    'sequence': 60,
    'summary': 'Kolyna MRP production scheduler',
    'version': '12.0.0.29',
    'description': """ Special MRP for Kolyna """,
    'website': 'https://www.dootix.com/',
    'depends': ['mrp', 'sale_subscription', 'dootix_partner'],
    'data': [
        'security/ir.model.access.csv',

        'views/production_schedule_views.xml',
        'views/mrp_production_plan_views.xml',
        'views/delivery_box_views.xml',
        'views/delivery_dates_views.xml',
        'views/res_dog_views.xml',

        'data/data.xml',

        'wizard/mo_merge_views.xml',
        'wizard/mo_delete_views.xml',
    ],
    'author': "Dootix Sàrl",
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'kolyna_mrp/static/src/js/grid.js',
            'kolyna_mrp/static/src/js/rations.js',
            'kolyna_mrp/static/src/scss/mrp.scss',
        ],
        'web.assets_qweb': [
            'kolyna_mrp/static/src/xml/grid.xml',
        ],
    }
}
