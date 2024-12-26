odoo.define('kolyna_theme.kolyna_events', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

var coefficient = {
    'XL': 4.25,
    'L': 3.25,
    'M': 2.75,
    'S': 2.25
}
var pricePerOffer = {
    'sp': 9.17,
    'p': 4.47,
}
var priceOfferWithIntolerances = {
    'sp': 10.37,
    'p': 5.67,
}
var pricePerDog = 70.56;
var pageStep = 1;


publicWidget.registry.KolynaRegistrationForm = publicWidget.Widget.extend({
    selector: '#kolyna',
    events: {
        'change input.oe_ration_type': '_onChangeRation',
        'change input#dog_weight': '_onChangeWeight',
        'change #select_offer': '_updateAmountLabel',
        'change .form_fre': '_updateAmountLabel',
        'change .ingredients': '_updateAmountLabel',
        'click .nextbutton': 'goNext',
        'click .prebutton': 'goPre',
        'change .form_ing': '_displayOther',
        'change .form_barf': '_fedUsingBarf',
        'change .form_advise': '_isAdvice',
        'change #del_mode': '_delMode',
        'change .form_order_dog': '_onlyOrder',
        'click .submitbutton': '_submitForm',
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        this.$el.find('input.oe_ration_type').trigger('change');
        return def;
    },

    _getOfferPrice: function(offer){
        var offerPrice = 0;
        if (this.$el.find('.ingredients input:checked').length <= 0) {
            offerPrice = _.has(pricePerOffer, offer) ? pricePerOffer[offer] : 4.47;
        } else {
            offerPrice = _.has(priceOfferWithIntolerances, offer) ? priceOfferWithIntolerances[offer] : 4.47;
        }
        return offerPrice;
    },

    _getAmountValue: function(){
        var offer = this.$el.find('#select_offer').val();
        var deliveryMode = this.$el.find('#del_mode').val();
        var deliveryFrequency = this.$el.find('.form_fre label input:checked').val();
        var dailyRationValue = this.$el.find('.ration_value input').val();
        var offerPrice = this._getOfferPrice(offer);

        var base = deliveryMode === 'home' ? 13.5 : 8.5;
        var deliveryCost = base * 2;
        var dailyRationInKG = (dailyRationValue/1000).toFixed(2);
        var monthlyRationValue =  (dailyRationInKG * 30.4).toFixed(2);

        var coefficientDelivery = 0.8 + offerPrice // amount_intolerances  TODO implement

        if (deliveryFrequency === 'weekly')
            deliveryCost = base * 4;
        if (deliveryFrequency === 'monthly')
            deliveryCost = base;
        if (deliveryFrequency === 'bi-monthly')
            deliveryCost = base*2;

        var amount = Math.ceil(coefficientDelivery*monthlyRationValue + deliveryCost + pricePerDog);
        return amount;

    },

    _updateAmountLabel: function() {
        this._updateLabel();
        var $input = this.$el.find('input.monthly_amount');
        var $label = this.$el.find('label.monthly_amount');
        var value = this._getAmountValue();
        $input.val(value);
        $label.text(value);
    },

    _getDialyRationValue: function(rationValue){
        var value = _.has(coefficient, rationValue) ? coefficient[rationValue] : 1.25;
        var dogWeight = this.$el.find('.form_weight input').val();
        var dailyRation = Math.floor(dogWeight * value * 10 * 100)/100;
        return dailyRation;
    },

    _onChangeRation:  async function (ev) {
        ev.preventDefault();
        var rationValue = $(ev.currentTarget).attr('value');
        var dailyRation = this._getDialyRationValue(rationValue);
        this._updateDailyRation(dailyRation);
    },

    _updateDailyRation: function(value){
        var $input = this.$el.find('.ration_value input');
        var $label = this.$el.find('.ration_value label');
        $label.text(value);
        $input.val(value);
    },

    _onChangeWeight: function(ev){
        ev.preventDefault();
        var rationValue = $(ev.currentTarget).attr('value');
        var dailyRation = this._getDialyRationValue(rationValue);
        this._updateDailyRation(dailyRation);
    },

    // get next page id
    _getNextPageID: function(current_page_id){
        var nextPageId = current_page_id + pageStep;
        if (current_page_id === 2 && this.$el.find('#select_offer option:selected').val() === 's')
            nextPageId = nextPageId + pageStep;
        return nextPageId;
    },

    // get previous page id
    _getPreviousPageID: function(current_page_id){
        var previousPageId = current_page_id - pageStep;
        if (current_page_id === 4 && this.$el.find('#select_offer option:selected').val() === 's')
            previousPageId = previousPageId - pageStep;
        return previousPageId;
    },

    // next button click
    goNext: function(ev){
        ev.preventDefault();
        this._updateAmountLabel();
        var id = $(ev.currentTarget).attr('current-id');
        var next_id = this._getNextPageID(parseInt(id));
        var cur_page = '.page_' + id;
        var next_page = '.page_' + next_id;

        // validate this page
        var page = ('page_' + id);
        var value = validations[page]();
        if(value) {
            $(cur_page).hide();
            $(next_page).show();
        }
    },

    // previous button click
    goPre: function(ev){
        ev.preventDefault();
        var id = $(ev.currentTarget).attr('current-id');
        var pre_id = this._getPreviousPageID(parseInt(id));
        var cur_page = '.page_' + id;
        var pre_page = '.page_' + pre_id;

        $(cur_page).hide();
        $(pre_page).show();
    },

    // display label if radio value true
    _onlyOrder: function(){
        $(this).val() === 'n' ? $('.label_radio').show() : $('.label_radio').hide();
    },

    // display label if using barf is true
    /*function _fedUsingBarf() {
        $(this).val() === 'n' ? $('.lable_radio_barf').show() : $('.lable_radio_barf').hide();
    },*/

    // display partner if advise value is true
    _isAdvice: function(){
        $(this).val() === 'y' ? $('.form_partner').show() : $('.form_partner').hide();
    },

    // display text input if other checkbox is checked
    _displayOther: function() {
        var checked = $("input[value='7']").is(':checked');
        checked ? ($('.opt_other').show(), $('.label_ingredients_other').show()) : ($('.opt_other').hide(), $('.label_ingredients_other').show())
    },

    // display partners if delivery mode is not home
    _delMode: function(){
        this._updateAmountLabel();
        var selected = $('#del_mode option:selected').val();
        this.$el.find('.form_fre input[type="radio"][value="weekly"]').closest('div').show();
        if (selected == 'home') {
            $('.all_partner').hide();
            $('.all_home').show()
            $('.all_warehouse').hide();
            this.$el.find('.form_fre input[type="radio"][value="monthly"]').trigger('click');
            this.$el.find('.form_fre input[type="radio"][value="weekly"]').closest('div').hide();
        }
        if (selected == 'pickup') {
            $('.all_partner').show();
            $('.all_home').hide()
            $('.all_warehouse').hide();
        }
        if (selected == 'warehouse') {
            $('.all_partner').hide();
            $('.all_home').hide()
            $('.all_warehouse').show()
        }
        if (!selected){
            $('.all_partner').hide();
            $('.all_home').hide();
            $('.all_warehouse').hide();
        }
    },

    // update labels as per offers selected
    _updateLabel: function(){
        var selected = $('#select_offer option:selected').val();
        var using_barf = $("input[name='fed_using_barf']:checked").val();
        if (selected === 's') {
            if (using_barf == 'y') {
                $('.label_info_std').show();
                $('.label_info_std_no_barf').hide();
                $('.label_info_pre').hide();
                $('.label_info_pre_no_barf').hide();
                $('.label_info_swiss_pre').hide();
                $('.label_info_swiss_pre_no_barf').hide();
            } else {
                $('.label_info_std').hide();
                $('.label_info_std_no_barf').show();
                $('.label_info_pre').hide();
                $('.label_info_pre_no_barf').hide();
                $('.label_info_swiss_pre').hide();
                $('.label_info_swiss_pre_no_barf').hide();
            }
            this.$el.find('.ingredients input').prop('checked', false);
        } else if (selected === 'sp') {
            if (using_barf == 'y') {
                $('.label_info_std').hide();
                $('.label_info_std_no_barf').hide();
                $('.label_info_pre').hide();
                $('.label_info_pre_no_barf').hide();
                $('.label_info_swiss_pre').show();
                $('.label_info_swiss_pre_no_barf').hide();
            } else {
                $('.label_info_std').hide();
                $('.label_info_std_no_barf').hide();
                $('.label_info_pre').hide();
                $('.label_info_pre_no_barf').hide();
                $('.label_info_swiss_pre').hide();
                $('.label_info_swiss_pre_no_barf').show();
            }
        } else {
            if (using_barf == 'y') {
                $('.label_info_std').hide();
                $('.label_info_std_no_barf').hide();
                $('.label_info_pre').show();
                $('.label_info_pre_no_barf').hide();
                $('.label_info_swiss_pre').hide();
                $('.label_info_swiss_pre_no_barf').hide();
            } else {
                $('.label_info_std').hide();
                $('.label_info_std_no_barf').hide();
                $('.label_info_pre').hide();
                $('.label_info_pre_no_barf').show();
                $('.label_info_swiss_pre').hide();
                $('.label_info_swiss_pre_no_barf').hide();
            }
        }
    },

    // submit form if term and condition checkbox is true
    _submitForm: function(ev){
        ev.preventDefault();
        if (confirmSubmit()) {
            window.dataLayer = window.dataLayer || [];
            var name = '';
            if (this.$el.find('#select_offer').val() == 's') {
                name = 'Standard';
            }
            if (this.$el.find('#select_offer').val() == 'sp') {
                name = 'Swiss Premium';
            }
            if (this.$el.find('#select_offer').val() == 'p') {
                name = 'Premium';
            }
            var dataToTransfer = {
                'event': 'ecomEvent',
                'transactionId': this._makeid(32), // valeur unique
                'transactionAffiliation': 'babarf.ch',
                'transactionTotal': this._getAmountValue(),
                'transactionCurrency': 'CHF', // CHF pour la Suisse
                'transactionProducts': [{
                    'sku': '1', // valeur unique du produit
                    'name': name +"-"+ this.$el.find('.form_fre label input:checked').val(),
                    'price': this._getAmountValue(),
                    'currency': 'CHF', // CHF pour la Suisse
                    'quantity': 1,
                    'category': this.$el.find('#del_mode').val(),
                }]
            };
            window.dataLayer.push(dataToTransfer);
            $("#kolyna_form").submit();
        }
    },

    _makeid: function(length){
       var result           = '';
       var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
       var charactersLength = characters.length;
       for ( var i = 0; i < length; i++ ) {
          result += characters.charAt(Math.floor(Math.random() * charactersLength));
       }
       return result;
    },

});

// fields validations
var validations = {
    page_1: function () {
        var dog_name = $.trim($("input[name='dogname']").val());
        $(".form_name").css("background-color", dog_name ? "#FFF" : "#F8CCCB");
        return dog_name != "";
    },
    page_2: function () {
        return true;
    },
    page_3: function () {
        return true;
    },
    page_4: function () {
        var del_mode = $('#del_mode option:selected').val();
        var delivered_partner = $('#delivered_partner option:selected').val();

        $("#del_mode").css("background-color", del_mode ? "#FFF" : "#F8CCCB");
        if (!del_mode || (del_mode == 'pickup' && !delivered_partner)) {
            $("#delivered_partner").css("background-color", delivered_partner ? "#FFF" : "#F8CCCB");
            return false;
        }
        else{
            return true;
        }
    },
    page_5: function () {
        var fname = $.trim($("input[name='fname']").val());
        var name = $.trim($("input[name='name']").val());
        var email = $.trim($("input[name='email']").val());
        var cemail = $.trim($("input[name='cemail']").val());
        var phone = $.trim($("input[name='phone']").val());
        var address = $.trim($("input[name='address']").val());
        var npa = $.trim($("input[name='npa']").val());
        var city = $.trim($("input[name='city']").val());
        $(".form_fullname").css("background-color", fname && name ? "#FFF" : "#F8CCCB");
        $(".form_email").css("background-color", email ? "#FFF" : "#F8CCCB");
        $(".form_cemail").css("background-color", cemail ? "#FFF" : "#F8CCCB");
        $(".form_phone").css("background-color", phone ? "#FFF" : "#F8CCCB");
        $(".form_address").css("background-color", address ? "#FFF" : "#F8CCCB");
        $(".form_npa").css("background-color", npa ? "#FFF" : "#F8CCCB");
        $(".form_city").css("background-color", city ? "#FFF" : "#F8CCCB");
        
        if (!fname || !name || !email || !cemail || !phone || !address || !npa || !city) {
            return false;
        }

        $(".form_email").css("background-color", (email == cemail) ? "#FFF" : "#F8CCCB");
        $(".form_cemail").css("background-color", (email == cemail) ? "#FFF" : "#F8CCCB");
        
        return email == cemail;

    },
    page_6: function () {
        var confirm = $('.form_checkbox_confirm input:checked').length;
        $(".form_checkbox_confirm").css("background-color", email ? "#FFF" : "#F8CCCB");
        if (confirm) {return true;} else {return false;}
    },
};

//  term and condition checkbox validation
var confirmSubmit = function() {
    var confirm = $('.form_checkbox_confirm input').is(":checked");
    $(".form_checkbox_confirm").css("background-color", confirm ? "#FFF" : "#F8CCCB");
    if (confirm){
        $('.btn-submit').prop('disabled', true);
    }
    return confirm;
};

});
