# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_employee_id = fields.Many2one(
        string='Sale Employee',
        comodel_name='hr.employee',
        readonly=True,
        copy=False
    )
    barcode = fields.Char(string="Employee Code", store=False)
    barcode_stored = fields.Char(string="Code Saved", copy=False)
    delivery_employee_id = fields.Many2one(
        string='Delivery Employee',
        comodel_name='hr.employee',
        readonly=True,
        copy=False
    )
    delivery_barcode = fields.Char(string="Delivery Code", store=False)
    order_wd = fields.Selection(
        string='Order WD',
        selection=[('not_wd', 'Not-WD'), ('walk_in', 'Walk-in'),
                   ('delivery', 'Delivery')],
        compute='_compute_order_wd', store=True
    )
    delivery_date_out = fields.Datetime(
        string='Delivery Date Out',
        readonly=True
    )
    delivery_date_in = fields.Datetime(
        string='Delivery Date In',
        readonly=True
    )
    delivery_duration = fields.Char(
        string='Delivery Duration',
        compute='_compute_delivery_duration', store=True
    )
    area = fields.Selection(related="warehouse_id.crm_team_id.area")

    @api.depends('order_line')
    def _compute_order_wd(self):
        for order in self:
            order.order_wd = 'walk_in' if not \
                any(line.is_delivery for line in order.order_line) else 'delivery'

    @api.depends('delivery_date_in', 'delivery_date_out')
    def _compute_delivery_duration(self):
        for order in self:
            order.delivery_duration = ''
            if order.delivery_date_in and order.delivery_date_out:
                difference = order.delivery_date_in - order.delivery_date_out
                duration_in_s = difference.total_seconds()

                days = divmod(duration_in_s, 86400)
                hours = divmod(days[1], 3600)
                minutes = divmod(hours[1], 60)
                seconds = divmod(minutes[1], 1)

                if days[0] == 0:
                    order.delivery_duration = "%d:%d:%d" % (
                        hours[0], minutes[0], seconds[0])
                else:
                    order.delivery_duration = "%d %d:%d:%d" % (
                        days[0], hours[0], minutes[0], seconds[0])

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()

        invoice_vals['order_wd'] = self.order_wd
        invoice_vals['sale_employee_id'] = self.sale_employee_id.id

        return invoice_vals

    @api.onchange('barcode')
    def _onchange_employee_barcode(self):
        if self.barcode == "****" and self.sale_employee_id:
            return

        if self.barcode and self.team_id:
            employee = self.env['hr.employee'].search([('barcode', '=', self.barcode), 
                                                       ('is_sale', '=', True),
                                                       ('crm_team_id', '=', self.team_id.id)])

            if not employee:
                raise ValidationError(_('Wrong Sales Code.'))
            else:
                self.sale_employee_id = employee
                self.barcode_stored = self.barcode
                self.barcode = "****"

    @api.onchange('delivery_barcode')
    def _onchange_delivery_barcode(self):
        if self.delivery_barcode == "****" and self.delivery_employee_id:
            return

        if self.delivery_barcode and self.area:
            employee = self.env['hr.employee'].search([('barcode', '=', self.delivery_barcode),
                                                       ('delivery_area', '=', self.area)])

            if not employee:
                raise ValidationError(_('Wrong Delivery Code.'))
            else:
                self.delivery_employee_id = employee
                self.delivery_barcode = "****"

                # Add Delivery line
                carrier_id = self.env.ref('set_shipping_cost.fixed_delivery_carrier')
                delivery_line = self.order_line.filtered(lambda line: line.is_delivery == True)

                if delivery_line:
                    self.order_line = [(2, delivery_line.id)]

                self.carrier_id = carrier_id

                if self.partner_id:
                    # set delivery detail in the customer language
                    carrier = carrier_id.with_context(lang=self.partner_id.lang)

                # Apply fiscal position
                taxes = carrier.product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
                taxes_ids = taxes.ids

                if self.partner_id and self.fiscal_position_id:
                    taxes_ids = self.fiscal_position_id.map_tax(
                        taxes, carrier.product_id, self.partner_id).ids

                # Create the sales order line
                price_unit = 10
                values = {
                    'name': "Shipping" if price_unit > 0 else "Free Shipping",
                    'product_uom_qty': 1,
                    'product_uom': carrier.product_id.uom_id.id,
                    'product_id': carrier.product_id.id,
                    'tax_id': [(6, 0, taxes_ids)],
                    'is_delivery': True,
                    'price_unit': price_unit
                }

                if carrier.invoice_policy == 'real':
                    values['price_unit'] = price_unit
                    values['name'] += _(' (Estimated Cost: %s )',
                                        self._format_currency_amount(price_unit))
                else:
                    values['price_unit'] = price_unit

                if carrier.free_over and self.currency_id.is_zero(price_unit):
                    values['name'] += '\n' + (_('Shipping') if price_unit > 0 else _("Free Shipping"))

                lines = [(0, 0, values)]

                self.order_line = lines
                self.delivery_message = False
                self.recompute_delivery_price = False

    def action_confirm(self):
        for order in self:
            if order.delivery_set and not order.delivery_employee_id:
                raise ValidationError(_("Please Choose Delivery First."))

            #Make delivery line last line
            if order.delivery_set:
                delivery_line = order.order_line.filtered(
                    lambda line: line.is_delivery == True)
                delivery_line.sequence = self.order_line[-1].sequence + 1

                #Delivery set on so
                order.delivery_date_out = datetime.now()
                
        return super(SaleOrder, self).action_confirm()
