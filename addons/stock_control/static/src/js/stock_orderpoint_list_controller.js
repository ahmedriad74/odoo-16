odoo.define('stock_control.stock_orderpoint_list_controller', function (require) {
    "use strict";

    var core = require('web.core');
    var StockOrderpointListController = require('stock.StockOrderpointListController');
    var qweb = core.qweb;

    StockOrderpointListController.include({
        /**
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            var $buttonOrderAll = this.$buttons.find('.o_button_order_all');
            $buttonOrderAll.on('click', this._onReplenishAll.bind(this));
        },
        _onReplenishAll: function () {
            var records = this.getSelectedRecords();
            this.model.replenish_all(records);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonOrderAll = this.$el.find('.o_button_order_all');
            if (this.getSelectedIds().length === 0){
                $buttonOrderAll.addClass('d-none');
            } else {
                $buttonOrderAll.removeClass('d-none');
            }
        },
    });
});
