odoo.define('kolyana_mrp.rations_tracker', function(require) {
    'use strict';

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var QWeb = core.qweb;
    var _t = core._t;

    var RationTrackers = AbstractAction.extend({
        template: 'RationTrackers',

        events: {
        },

        init: function(parent, action) {
            return this._super.apply(this, arguments);
        },

        willStart: function() {
            return this.fetch_rations_data();
        },

        start: function() {
            return this._super.apply(this, arguments);
        },

        fetch_rations_data: function() {
            var self = this;
            return this._rpc({
                route: '/mrp/production/rations/data',
                params: {
                },
            }).then(function(res) {
                self.days = res.days;
                self.dogs = res.dogs;
                self.matrix = res.matrix;
            });
        },
    });


    var RationTrackersSummary = AbstractAction.extend(ControlPanelMixin, {
        template: 'RationTrackersSummary',

        events: {
        },

        init: function(parent, action) {
            this.selected_filter = [];
            return this._super.apply(this, arguments);
        },

        willStart: function() {
            return this.fetch_rations_summary_data();
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._updateControlPanel();
            });
        },

        fetch_rations_summary_data: function() {
            var self = this;
            return this._rpc({
                route: '/mrp/production/rations/summary/data',
                params: {
                    selected_filter: self.selected_filter
                },
            }).then(function(res) {
                self.dogs = res.dogs;
                self.selected_filter = res.selected_filter;
            });
        },

        // Updates the control panel and render the elements that have yet to be rendered
        _updateControlPanel: function() {
            var self = this;

            this.$searchview_buttons = $(QWeb.render("RationTrackerFilter", {selected_filter: this.selected_filter}));
            this.$searchview_buttons.find('.o_filters_menu').bind('click', function(ev) {
                self._applyFilter(ev);
            });

            this.update_control_panel({
                cp_content: {
                    $searchview_buttons: this.$searchview_buttons,
                },
            });
        },
        re_renderElement: function() {
            var self = this;
            this.$el.html(QWeb.render('RationTrackersSummary', {widget: this}));
            self._updateControlPanel();
        },

        _applyFilter: function(event) {
            var self = this;
            var $elem = $(event.target);
            $elem.toggleClass('selected');
            this.selected_filter = this.$searchview_buttons.find('.o_filters_menu a.selected.group').map(function () {return $(this).data('value')}).get();
            return this.fetch_rations_summary_data().then(function() {
                self.re_renderElement();
            });
        },
    });

    core.action_registry.add("ration_tracker", RationTrackers);
    core.action_registry.add("ration_tracker_summary", RationTrackersSummary);

    return {
        RationTrackers: RationTrackers,
        RationTrackersSummary: RationTrackersSummary,
    }
});