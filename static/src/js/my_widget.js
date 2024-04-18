odoo.define('custom_module.one2many_search', function (require) {
    "use strict";

    var core = require('web.core');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fieldRegistry = require('web.field_registry');

    var _t = core._t;

    var One2ManySearchWidget = FieldOne2Many.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.searchValue = "";
        },
        _search: function () {
            var self = this;
            var domain = [];
            if (this.searchValue) {
                domain.push(['name', 'ilike', this.searchValue]);
            }
            this.trigger_up('reload', {
                domain: domain,
                callback: function (res) {
                    self.trigger_up('value_changed', {
                        value: res
                    });
                }
            });
        },
        _renderSearchBar: function () {
            var self = this;
            var $searchBar = $('<input type="text" class="o_input o_search_input">')
                .attr('placeholder', _t("Search..."))
                .on('input', function (ev) {
                    self.searchValue = ev.target.value;
                    self._search();
                });
            this.$('.o_form_field_one2many_search').append($searchBar);
        },
        _renderEditButton: function () {
            // Override this method if you want to customize the rendering of the Edit button
        },
        _render: function () {
            this._super.apply(this, arguments);
            if (this.mode === 'readonly') {
                this.$el.addClass('o_readonly');
                this.$el.find('.o_form_field_one2many_search').remove();
            }
        },
        _renderReadonly: function () {
            this._super.apply(this, arguments);
            this._renderSearchBar();
        },
        _renderEdit: function () {
            this._super.apply(this, arguments);
            this._renderSearchBar();
        }
    });

    fieldRegistry.add('one2many_search', One2ManySearchWidget);

    return {
        One2ManySearchWidget: One2ManySearchWidget
    };

});
