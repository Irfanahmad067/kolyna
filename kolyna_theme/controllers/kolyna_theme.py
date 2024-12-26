from odoo import http
from odoo.http import request
from odoo.fields import Datetime
import logging
import json

class themeKolynaController(http.Controller):

    def _create_order(self, dog, post):
        order_lines = [(0, 0, {
            'product_id': request.env.ref('kolyna_sale.product_abonnement_mensuel').id,
            'dog_id': dog.id,
            'price_unit': dog.amount
        })]

        if post.get('fed_using_barf') == 'n':
            order_lines.append((0, 0, {
                'product_id': request.env.ref('kolyna_sale.product_starter_kit').id,
                'dog_id': dog.id,
                'price_unit': dog.weight * 2.35,
                'discount': 100,  # free products
            }))

        vals = {
            'partner_id': post.get('partner_id'),
            'order_line': order_lines,
            'user_id': 2
        }

        return request.env['sale.order'].sudo().create(vals)

    @http.route('/forms/registration', type="http", auth="public", website=True)
    def theme_kolyna_controller(self, **post):
        if 'from' in request.params:
            source = request.params['from']
        else:
            source = ''
        
        dogs = request.env['res.dog']
        default_weight = dogs._fields['weight'].default(dogs)
        # ['Very big ration','Big ration','Standard ration','Small ration','Very small ration']
        desired_ration = dogs._fields['desired_ration']._description_selection(request.env)
        for ration in desired_ration:
            if ration[0] == 'XS':
                desired_ration.remove(ration)
        our_offers = dogs._fields['offer']._description_selection(request.env)
        ingredients = request.env['res.dog.intolerance'].sudo().search_read([], ['name', 'coefficient'])
        delivery_mode = dogs._fields['delivery_mode']._description_selection(request.env)
        pickups = request.env['res.partner'].sudo().search(
            [('is_pickup', '=', True)], order='name ASC')
        partners = request.env['res.partner'].sudo().search(
            [('is_prescriber', '=', True)], order='name ASC')
        delivery_frequency = dogs._fields['delivery_frequency']._description_selection(request.env)
        
        if source == 'standard':
            offer_default = 's'
        elif source == 'premium':
            offer_default = 'p'
        elif source == 'swiss':
            offer_default = 'sp'
        else:
            offer_default = dogs._fields['offer'].default(dogs)
        default_no_barf = True    
        if source == 'no_barf':
            default_no_barf = False

        return request.render('kolyna_theme.kolina_theme_template', {
            'default_weight': default_weight,
            'desired_ration': desired_ration,
            'pickups': pickups,
            'desired_ration_default': dogs._fields['desired_ration'].default(dogs),
            'our_offers': our_offers,
            'our_offers_default': offer_default,
            'ingredients': ingredients,
            'delivery_mode': delivery_mode,
            'delivery_mode_default': dogs._fields['delivery_mode'].default(dogs),
            'partners': partners,
            'default_no_barf': default_no_barf,
            'delivery_frequency': delivery_frequency,
            'delivery_frequency_default': dogs._fields['delivery_frequency'].default(dogs),
        })

    @http.route('/forms/starter_kit_submit', type="http", auth="public", method="POST", website=True)
    def theme_kolyna_form_submit(self, **post):
        ingredients = request.httprequest.form.getlist("ingredients")

        already_barf = False
        if post.get('fed_using_barf', False) == 'y':
            already_barf = True

        partner_name = post.get('fname', "") + ' ' + post.get('name', "")
        
        is_advice = post.get('is_advice', False) or False
        prescriber = post.get('advice_partner', False) or False
        
        if is_advice == 'n':
            prescriber = False
        
        partner = request.env['res.partner'].sudo().create({
            'name': partner_name,
            'street': post.get('address', False) or False,
            'phone': post.get('phone', False) or False,
            'city': post.get('city', False) or False,
            'zip': post.get('npa', False) or False,
            'email': post.get('email', False) or False,
            'prescriber': prescriber,
        })
        
        post['partner_id'] = partner.id
        
        daily_ration_g = int(float(post.get('daily_ration_g', False)))
        
        pickup_point = post.get('delivered_partner', False)
        
        if post.get('delivered_to', False) == 'home':
            pickup_point = ''
        else:
            pickup_point= post.get('delivered_partner', False)
        
        delivered_to = post.get('delivered_to', False)
        if delivered_to == 'warehouse':
            pickup_point = 4114
             

        dog = request.env['res.dog'].sudo().create({
            'name': post.get('dogname', False) or False,
            'breed': post.get('breed_name', False) or False,
            'already_barf': already_barf,
            'birth_date': post.get('birthdate', False) or False,
            'weight': post.get('dog_weight', False) or False,
            'owner': post.get('partner_id', False) or False,
            'desired_ration': post.get('ration_type', False) or False,
            'daily_ration_g': str(daily_ration_g) or False,
            'daily_ration_kg': str(daily_ration_g / 1000) or False,
            'monthly_ration_kg': str(daily_ration_g / 1000 * 30.4) or False,
            'offer': post.get('offer', False) or False,
            'remark': post.get('remark', False) or False,
            'intolerances_others': post.get('other', False) or False,
            'delivery_mode': post.get('delivered_to', False) or False,
            'pickup_point': pickup_point or False,
            'delivery_frequency': post.get('fre_type', False) or False,
            'intolerances_ids': [(6, 0, [int(ids) for ids in ingredients])],
            'preorder_receipt_date': Datetime.now(),
            'mensual_amount': 0,
        })
        
        dog.amount = dog.get_correct_price()
        
        #dogs = request.env['res.dog']
        
        # list_offers = dogs._fields['offer']._description_selection(request.env)
        # for temp_offer in list_offers:
        #     if dog.offer in temp_offer:
        #         offer = temp_offer[1]
        
        # list_delivery_mode = dogs._fields['delivery_mode']._description_selection(request.env)
        # for temp_delivery_mode in list_delivery_mode:
        #     if dog.delivery_mode in temp_delivery_mode:
        #         delivery_mode = temp_delivery_mode[1]
        
        # list_delivery_frequency = dogs._fields['delivery_frequency']._description_selection(request.env)
        # for temp_delivery_frequency in list_delivery_frequency:
        #     if dog.delivery_frequency in temp_delivery_frequency:
        #             delivery_frequency = temp_delivery_frequency[1]
                    
        # if dog.pickup_point:
        #     pickup = dog.pickup_point.company_name
        # else:
        #     pickup = ''
        
        # my_values = {
        #     'first_name' : partner.firstname,
        #     'last_name' : partner.lastname,
        #     'dog_name' : dog.name,
        #     'dog_id' : dog.id,
        #     'customer_id' : partner.id,
        #     'daily_ration' : int(dog.daily_ration_g),
        #     'offer' : offer,
        #     'ingredients' : ", ".join(intolerance.name for intolerance in dog.intolerances_ids),
        #     'delivery_mode' : delivery_mode,
        #     'delivery_frequency' : delivery_frequency,
        #     'address' : partner.street + " - " +partner.zip + " - " +partner.city,
        #     'amount' : dog.amount,
        #     'phone': partner.phone,
        #     'pickup': pickup,
        #     'remark': dog.remark,
        # }
        
        # body = """<h3>Bonjour %(first_name)s %(last_name)s,</h3>
        #     <p>Nous avons bien enregistré votre pré-commande pour %(dog_name)s.</p>
        #     <p>Étant actuellement en phase de lancement nous ne serons pas immédiatement en
        #     mesure de livrer tous nos clients, mais nous vous recontacterons au plus vite suivant
        #     l’augmentation de nos capacités de production.</p>
        #     <p>Vous aurez l’occasion de confirmer, annuler, ou modifier votre commande à ce moment
        #     là si désiré.</p>
        #     <p>Dans l’intervalle, n’hésitez pas à suivre l’avancée de notre projet via les pages suivantes :</p>
        #     <p><a href="https://www.babarf.ch/news/">Les news</a><br />
        #     <a href="https://www.facebook.com/babarf.ch">Facebook</a><br />
        #     <a href="https://www.instagram.com/babarf_ch/">Instagram</a><br /><br />
        #     À bientôt !</p>
        #     <p>L’équipe Babarf</p>
        #     <p><center><img src="https://www.babarf.ch/wp-content/uploads/2019/05/LOGO-2663px.png" width="200px" /></center></p>
        #     <p><strong>Voici un résumé de votre abonnement pour %(dog_name)s :</strong><br /><br />
        #     Numéro de client : %(customer_id)s<br />
        #     Ration quotidienne : %(daily_ration)s grammes<br />
        #     Offre choisie : %(offer)s<br />
        #     Ingrédients nons désirés : %(ingredients)s<br />
        #     Mode de livraison : %(delivery_mode)s<br />
        #     Fréquence des livraisons : %(delivery_frequency)s<br />
        #     Point retrait sélectionné (si applicable): %(pickup)s<br />
        #     Remarques complémentaires: %(remark)s<br /><br />
        #     Vos coordonnées :<br />
        #     %(first_name)s %(last_name)s<br />
        #     %(address)s<br />
        #     %(phone)s<br /><br />
        #     Coût mensuel total : %(amount)s CHF</p>""" % my_values
        
        # template_obj = request.env['mail.mail']
        # template_data = {
        #                 'subject': 'Babarf - Votre pré-commande',
        #                 'body_html': body,
        #                 'email_to': partner.email,
        #                 'email_cc': "info@babarf.ch",
        #                 'email_from' : 'info@babarf.ch',
        #                 }
        # template_id = template_obj.create(template_data)
        # template_id.send()

        request.env.ref('kolyna_theme.email_template_dog').sudo().send_mail(dog.id, force_send=True)

        self._create_order(dog, post)

        return request.redirect('https://www.babarf.ch/un-grand-merci/')
