# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def action_cancel(self):
        for this in self:
            # if this.picking_type_id and this.picking_type_id.code == 'internal' and this.state != 'draft' and \
            #         (this.location_id and this.location_dest_id and this.location_id.id != this.location_dest_id.id):
            #     new_pickings = this._ro_create_picking()
            #     for pick in new_pickings:
            #         if this.group_id and this.origin != 'Manual Replenishment':

            #             # get the stock_control user to assign the activity
            #             stock_control_user = self.env['res.users'].search(
            #                 [('is_stock_control', '=', True)])

            #             if not stock_control_user:
            #                 raise UserError(_("Choose a stock control user."))

            #             for stock_user in stock_control_user:
            #                 data = {
            #                     'res_id': pick.id,
            #                     'res_model_id': self.env.ref('stock.model_stock_picking').id,
            #                     'user_id': stock_user.id,
            #                     'summary': 'Picking Need to change location',
            #                     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            #                     'date_deadline': fields.Date.today(),
            #                 }
            #                 self.env['mail.activity'].create(data)
            #         else:
            #             member_ids = pick.location_dest_id.get_warehouse().crm_team_id.member_ids
            #             for team_user in member_ids:
            #                 data = {
            #                     'res_id': pick.id,
            #                     'res_model_id': self.env.ref('stock.model_stock_picking').id,
            #                     'user_id': team_user.id,
            #                     'summary': 'Picking Need to change location',
            #                     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            #                     'date_deadline': fields.Date.today(),
            #                 }
            #                 self.env['mail.activity'].create(data)
            
            # else:
            activities = self.env['mail.activity'].search(
                [('res_id', '=', this.id)])
            for activity in activities:
                activity.with_user(SUPERUSER_ID).action_done()

        res = super(StockPicking, self).action_cancel()
        return res

    # Create backorder with draft status
    def _ro_create_picking(self):

        new_pickings = self.env['stock.picking']
        new_moves = self.env['stock.move']

        for picking in self:
            
            res = picking.move_lines
        
            for rec in res:
                
                move_id = self.env['stock.move'].with_user(SUPERUSER_ID).create({
                    'name': rec.name,
                    'product_id': rec.product_id.id,
                    'description_picking': rec.description_picking,
                    'product_uom': rec.product_uom.id,
                    'product_uom_qty': rec.product_uom_qty,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.location_dest_id.id,
                    'picking_type_id': rec.picking_type_id.id,
                    'origin': False,
                    'partner_id': False
                })

                new_moves |= move_id

            if new_moves:
                new_picking = new_pickings.create({
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.location_dest_id.id,
                    'picking_type_id': rec.picking_type_id.id
                })
                new_moves.write({'picking_id': new_picking.id})

                picking.message_post(
                    body=_('The new picking <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        new_picking.id, new_picking.name))

                new_pickings |= new_picking

        return new_pickings

    def mass_buy_from_po(self):
        for this in self:
            self.env['purchase.order'].create({'partner_id': self.env.user.partner_id.id,
                                               'picking_type_id': this.picking_type_id.id,
                                               'order_line': [(0, 0, {'product_id': x.product_id.id, 'product_qty': x.product_uom_qty}) for x in this.move_lines],
                                               })
