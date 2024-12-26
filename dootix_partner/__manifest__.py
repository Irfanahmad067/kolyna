# -*- coding: utf-8 -*-
{
    'name': "Partner fields for Kolyna, by Dootix",

    'summary': "Adding special fields to partners and creating model res.dog",

    'author': "Dootix",
    'website': "https://www.dootix.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    
    #The x.y.z version numbers follow the semantics breaking.feature.fix:
    #x increments when the data model or the views had significant changes. Data migration might be needed, or depending modules might be affected.
    #y increments when non-breaking new features are added. A module upgrade will probably be needed.
    #z increments when bugfixes were made. Usually a server restart is needed for the fixes to be made available.
    'version': '18.0.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'mail', 'web_map'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/dog.xml',
        'data/ration_cron.xml',
    ],
    'auto_install': False,
    'installable': True,
}
