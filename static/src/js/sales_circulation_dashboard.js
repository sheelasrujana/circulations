odoo.define('sales_circulation.sales_circulation_dashboard', function (require){
"use strict";
var AbstractAction = require('web.AbstractAction');
var Widget = require('web.Widget');
var core = require('web.core');
var QWeb = core.qweb;

var SalesCirculationDashBoard = AbstractAction.extend({
   template: 'sales_circulation_dashboards',
   init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['sales_circulation_dashboard_data'];
        this.today_sale = [];
    },
    willStart: function() {
    var self = this;
    return $.when(this._super()).then(function() {
            return self.fetch_data();
        });
    },
    events: {
        'change .unit_name_selection': 'fetch_data',
    },

    display_filtered_val: function(){
        var unit_name = $('#unit_select_data').val();
        var from_date = $('#from_date').val();
        var to_date = $('#to_date').val();
        var def1 =  this._rpc({
            model: 'sales.circulation.dashboard.data',
            method: 'display_dashboard_vals',
            args: [[unit_name], from_date, to_date],
        }).then(function (result) {
            self.trigger_up('reload');
        });
        return $.when(def1);

    },
    start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
               self.render_dashboards();
            });
        },
        render_dashboards: function(){
        var self = this;
        _.each(this.dashboards_templates, function(template) {
                self.$('.o_pj_dashboard').append(QWeb.render(template, {widget: self}));
            });
        return self.fetchChartData();
    },

    fetchChartData: function () {
        var self = this;
        var user_id = this.getSession().uid;
        var Charts = self._rpc({
           model: "sales.circulation.dashboard.data",
           method: "get_invoice_line_vals",
           args: [[1],user_id],
        })
        .then(function (data) {
           //Product Pie Chart                  
           var ctx = document.getElementById('circulation_pie_chart').getContext('2d');
           const circulation_pie_chart = new Chart(ctx, {
              type: 'doughnut',
              data: {
                 labels: data.period_list,
                 datasets: [
                    {
                       label: 'Total Amount',
                       data: data.inv_total_amount_list,
                       borderWidth: 1,
                       backgroundColor: data.background_color,
                       borderColor: data.border_color
                    },
                     {
                        label: 'Amount Due',
                        data: data.inv_total_due_list,
                        borderWidth: 1,
                        backgroundColor: data.background_color2,
                        borderColor: data.border_color2
                     }
                 ]
              },
              options: {
              }
           });

           //Product Bar Graph
           var ctx = document.getElementById('circulation_bar_graph').getContext('2d');
           const circulation_bar_graph = new Chart(ctx, {                  
              type: 'bar',
              data: {
                 labels: data.inv_due_date_list,
                 datasets: [
                    {
                       label: 'Total Amount',
                       data: data.inv_total_amount_list,
                       borderWidth: 1,
                       backgroundColor: 'rgba(54, 162, 235, 0.6)',
                       // backgroundColor: data.background_color1,
                       // borderColor: data.border_color1
                    },
                    {
                       label: 'Amount Due',
                       data: data.inv_total_due_list,
                       borderWidth: 1,
                       backgroundColor: 'rgba(255, 99, 132, 0.6)',
                       // backgroundColor: data.background_color2,
                       // borderColor: data.border_color2
                    },
                 ]
              },
              options: {
              }
           });

           //Product Line Graph
           var ctx = document.getElementById('circulation_line_graph').getContext('2d');
           const circulation_line_graph = new Chart(ctx, {                  
              type: 'radar',
              data: {
                 labels: data.inv_due_date_list,
                 datasets: [
                    {
                       label: 'Total Amount',
                       data: data.inv_total_amount_list,
                       borderWidth: 1,
                       backgroundColor: 'rgba(54, 162, 235)',
                       borderColor: 'rgba(54, 162, 235)',
                       pointRadius:3,
                       // backgroundColor: data.background_color1,
                       // borderColor: data.border_color1,
                       fill:false,
                    },
                    {
                       label: 'Amount Due',
                       data: data.inv_total_due_list,
                       borderWidth: 1,
                       backgroundColor: 'rgba(255, 99, 132)',
                       borderColor: 'rgba(255, 99, 132)',
                       pointRadius:3,
                       // backgroundColor: data.background_color2,
                       // borderColor: data.border_color2,
                       fill:false,
                    }
                 ]
              },
              options: {
              }
           });
        });
        return Charts;
    },
    fetch_data: function() {
        var self = this;
        var unit_name = $('#unit_select_data').val();
        var from_date = $('#from_date').val();
        var to_date = $('#to_date').val();
        var def1 =  this._rpc({
                model: 'sales.circulation.dashboard.data',
                method: 'get_display_data',
                args: [unit_name, from_date, to_date],
        }).then(function(result)

        {
            self.total_amount = result['total_amount'],
            self.total_amount_due = result['total_amount_due'],
            self.total_demand_request = result['total_demand_request'],
            self.payment_collections_total = result['payment_collections_total'],
            self.total_commission_total = result['total_commission_total'],
            self.returns = result['returns'],
            self.total_copies_current_day = result['total_copies_current_day'],
            self.total_copies_previous_day = result['total_copies_previous_day'],
            self.account_deposit_total_amount = result['account_deposit_total_amount'],
            self.account_deposit_total_amount_outstanding = result['account_deposit_total_amount_outstanding'],
            self.transportation_bill_total_amount = result['transportation_bill_total_amount'],
            self.transportation_bill_total_amount_due = result['transportation_bill_total_amount_due'],
            self.indent_lines = result['indent_lines'],
            self.invoice_lines = result['invoice_lines'],
            self.invoice_obj = result['invoice_obj'],
            self.unit_many2many_id = result['unit_many2many_id'],
            self.user = result['user']
        });
        return $.when(def1);
    },

})
core.action_registry.add('sales_circulation_dashboard_tags', SalesCirculationDashBoard);
return SalesCirculationDashBoard;
});


$(document).ready(function(){
    $('body').delegate('.display_cio_div','click',function() {
        window.open($(".display_cio_div").attr("test"),'_blank');
    });
    $('body').delegate('.display_indent_demand','click',function() {
        window.open($(".display_indent_demand").attr("test"),'_blank');
    });
    $('body').delegate('.display_total_demand_request','click',function() {
        window.open($(".display_total_demand_request").attr("test"),'_blank');
    });
    $('body').delegate('.display_bill_invoices','click',function() {
        window.open($(".display_bill_invoices").attr("test"),'_blank');
    });
    $('body').delegate('.display_payment_collections_total','click',function() {
        window.open($(".display_payment_collections_total").attr("test"),'_blank');
    });
    $('body').delegate('.display_account_deposit_div','click',function() {
        window.open($(".display_account_deposit_div").attr("test"),'_blank');
    });
    $('body').delegate('.display_transportation_bill_div','click',function() {
        window.open($(".display_transportation_bill_div").attr("test"),'_blank');
    });
});


