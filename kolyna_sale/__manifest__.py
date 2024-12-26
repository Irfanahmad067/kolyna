# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kolyna Sales Customization',
    'category': 'Sales',
    'sequence': 60,
    'summary': 'Kolyna Sales Customization',
    'description': """

We need to add a column on the sale.order.line when creating a sale order and as well on the corresponding invoice.
line which will be created from the sale order The column will be indentified by “Dog”.
When selecting a customer, we can then add lines to the sale.order.line part.
When adding the following product : Abonnement mensuel Babarf (XML id __export__.product_template_64_0ed36907),
we can then choose in the column “Dog” one of the dog that is owned by this customer (and only the ones owned by the customer,
model res.dog, column owner defines the owner). When we choose this product, and a dog,
the price of this line is set to the column “amount” of the res.dog model.
It should create the same fields on the corresponding invoice.
This product is linked to a subscription, therefore each month it will create an invoice.
The amount of this line must take the value of amount EACH month, as it can change (because the dog can need more food,
or change of subscription plan, etc.). So the price of the line created by the subscription on the invoice must be taken each time an invoice is created.

    """,
    'website': 'https://www.odoo.com/',
    'depends': ['sale_subscription', 'dootix_partner'],
    'data': [
        'views/sale_views.xml',
        'views/account_invoice_views.xml',
        'data/data.xml',
    ],
    
    'installable': True,
    'auto_install': False,
}
