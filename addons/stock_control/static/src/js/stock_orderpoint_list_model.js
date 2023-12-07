odoo.define('stock_control.stock_orderpoint_list_model', function (require) {
    "use strict";
    
    var core = require('web.core');
    var StockOrderpointListModel = require('stock.StockOrderpointListModel');    
    var qweb = core.qweb;
    
    StockOrderpointListModel.include({
        replenish_all: function (records) {
            var self = this;
            var model = records[0].model;
            var recordResIds = _.pluck(records, 'res_id');
            var context = records[0].getContext();
            return this._rpc({
                model: model,
                method: 'action_replenish_all',
                args: [recordResIds],
                context: context,
            }).then(function () {
                return self.do_action('stock.action_replenishment');
            });
          },
    });  
});
    