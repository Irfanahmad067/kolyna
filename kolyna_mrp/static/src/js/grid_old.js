odoo.define('kolyana_mrp.mrp_schedule_production', function(require) {
    'use strict';

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var Dialog = require('web.Dialog');

    var QWeb = core.qweb;
    var _t = core._t;

    console.log("hello>>>>>>")

    var mrp_production_scheduler_grid = AbstractAction.extend({
        hasControlPanel: true,
        template: 'productionSchedulerGrid',

        events: {
            'change .o_psg_save_input_text': '_onChangeRationInput',
            'change .o_dog_row_checkbox': '_onDogRowSelect',
            'change .o_dog_select_all': '_onSelectAll',
        },

        init: function(parent, action) {
            this.selected_group = 'all';
            this.bag_size = '';
            this.piece_size = '';
            return this._super.apply(this, arguments);
        },

        willStart: function() {
            return this.fetch_matrix_data();
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._renderButtons();
                self._updateControlPanel();
            });
        },

        fetch_matrix_data: function() {
            var self = this;
            return this._rpc({
                route: '/mrp/production/schedule/data',
                params: {
                    selected_group: self.selected_group,
                    selected_bag_size: self.bag_size,
                    selected_piece_size: self.piece_size
                },
            }).then(function(res) {
                self.products = res.products;
                self.dogs = res.dogs;
                self.matrix = res.matrix;
                self.dog_group = res.dog_group;
                self.selected_group = res.selected_group;
                self.bag_sizes = res.bag_sizes;
                self.piece_sizes = res.piece_sizes;
                self.selected_bag_size = res.selected_bag_size;
                self.selected_piece_size = res.selected_piece_size;
            });
        },

        re_renderElement: function() {
            var self = this;
            this.$el.html(QWeb.render('productionSchedulerGrid', {widget: this}));
            self._renderButtons();
            self._updateControlPanel();
        },

        option_group: function(event) {
            var self = this;
            var $elem = $(event.target);
            $elem.toggleClass('selected');
            if ($elem.data('value') === 'all' && $elem.hasClass('selected')) {
                this.$searchview_buttons.find('.o_filters_menu a.selected.group').removeClass('selected');
                this.selected_group = 'all';
            }
            if ($elem.data('value') !== 'all') {
                this.$searchview_buttons.find('.o_filters_menu a.selected.all_group').removeClass('selected');
                this.selected_group = this.$searchview_buttons.find('.o_filters_menu a.selected.group').map(function () {return $(this).data('value')}).get();
            }
            return this.fetch_matrix_data().then(function() {
                self.re_renderElement();
            });
        },

        option_size: function() {
            var self = this;
            this.bag_size = this.$searchview_buttons.find("select[name='bag_size']").val();
            this.piece_size = this.$searchview_buttons.find("select[name='piece_size']").val();
            return this.fetch_matrix_data().then(function() {
                self.re_renderElement();
            });
        },

        _renderButtons: function() {
            var self = this;
            this.$buttons = $(QWeb.render("PSG.Buttons", {}));
            this.$buttons.siblings('button[data-createmo]').on('click', function(ev) {
                var $elem = $(ev.currentTarget);
                var createmo = $elem.data('createmo');
                self._saveGridData(createmo);
            });
            this.$buttons.siblings('button.attribute_menu').on('click', this._onClickAttributeMenu.bind(this));
            return this.$buttons;
        },

        // Updates the control panel and render the elements that have yet to be rendered
        _updateControlPanel: function() {
            var self = this;
            var psg_data = {
                groups: this.dog_group,
                selected_group: this.selected_group,
                bag_sizes: this.bag_sizes,
                piece_sizes: this.piece_sizes,
                selected_bag_size: this.selected_bag_size,
                selected_piece_size: this.selected_piece_size
            }

            this.$searchview_buttons = $(QWeb.render("PSG.optionButton", psg_data));
            this.$searchview_buttons.find('.o_filters_menu').bind('click', function(ev) {
                self.option_group(ev);
            });
            this.$searchview_buttons.find('.js_apply_filter').bind('click', this.option_size.bind(this));

            if (!this.$buttons) {
                this._renderButtons();
            }
            this.update_control_panel({
                cp_content: {
                    $buttons: this.$buttons,
                    $searchview_buttons: this.$searchview_buttons,
                },
            });
        },

        _saveGridData: function(createmo=false) {
            var self = this;
            this._rpc({
                route: '/mrp/production/schedule/save/data',
                params: {
                    matrix: JSON.stringify(this.matrix),
                    createmo: createmo
                }
            }).then(function(res) {
                self.do_notify(res);
                self.unsetRations();
            });
        },

        _updateMatrix: function(dogId, productId, value) {
            if (this.matrix[dogId]) {
                this.matrix[dogId][productId] = value;
            }
        },

        _onChangeRationInput: function(ev) {
            var $input = $(ev.currentTarget);
            var dogId = parseInt($input.data('dog'));
            var productId = parseInt($input.data('product'));
            var value = parseFloat($input.val());
            this._updateMatrix(dogId, productId, value);
        },
        _onDogRowSelect: function(ev) {
            var $attributeMenu = this.$buttons.siblings('.attribute_menu');
            if (this.$('.o_dog_row_checkbox:checked').length) {
                $attributeMenu.removeClass('d-none');
            } else {
                $attributeMenu.addClass('d-none');
            }
        },
        _onClickAttributeMenu: function() {
            var self = this;
            var $dialogTemplate = $(QWeb.render('AttributeMenuDialog', {widget: this}));
            var dialog = new Dialog(this, {
                size: 'large',
                title: _t("Attribute The Menu "),
                $content: $dialogTemplate,
                buttons: [
                    {
                        text: _t("Apply"),
                        classes: 'btn-primary',
                        click: function () {
                            // set data to matrix
                            var dogIds = self.$('.o_dog_row_checkbox:checked').map(function() {return $(this).attr('data-dog')}).get();
                            _.each(self.products, function(product) {
                                var value = $dialogTemplate.find('input[data-product='+product[0]+']').val();
                                if (value) {
                                    _.each(dogIds, function(dogId) {
                                        self.$('input[data-dog='+parseInt(dogId)+'][data-product='+product[0]+']').val(parseFloat(value)).change();
                                    });
                                }
                            });
                            //clear checkbox
                            self.$('.o_dog_row_checkbox:checked').prop('checked', false).change();
                            self.$('.o_dog_select_all:checked').prop('checked', false).change();
                        },
                        close: true
                    },
                    {
                        text: _t("Cancel"),
                        close: true,
                    },
                ],
            });
            dialog.open();
        },
        _onSelectAll: function(ev) {
            if($(ev.currentTarget).is(':checked')) {
                this.$('.o_dog_row_checkbox').prop('checked', true).change();
            } else {
                this.$('.o_dog_row_checkbox').prop('checked', false).change();
            }
        },
        unsetRations: function(ev) {
            this.$('.o_psg_save_input_text').val(0); // unset all
        },
    });

    core.action_registry.add("mrp_production_scheduler_grid", mrp_production_scheduler_grid);

    return mrp_production_scheduler_grid;
});