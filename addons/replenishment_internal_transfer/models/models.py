# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError
from itertools import groupby


class Picking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[
        ('validate2', 'Second Validate'),
        ('done', )])
    flag = fields.Boolean(default=True, copy=False)
    first_validate_date = fields.Datetime(string='First Validate Date')
    team_f_validate = fields.Many2one(comodel_name='crm.team', copy=False)

    def action_confirm(self):
        pickings = self.filtered(
            lambda p: p.picking_type_code == 'internal')

        if not self.env.user.has_group('stock.group_stock_manager') and pickings:
            mail_activity_data = []
            activities_to_finish = self.env['mail.activity'].search(
                [('res_id', 'in', pickings.ids)])
            activities_to_finish.with_user(SUPERUSER_ID).action_done()
            
            for picking in pickings:
                warehouse = picking.location_id.get_warehouse()
                member_ids = warehouse.crm_team_id.member_ids
                
                for team_user in member_ids:
                    data = {
                        'res_id': picking.id,
                        'res_model_id': self.env.ref('stock.model_stock_picking').id,
                        'user_id': team_user.id,
                        'summary': 'Product Request Schedule',
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': fields.Date.today(),
                    }
                    mail_activity_data.append(data)

            self.env['mail.activity'].create(mail_activity_data)

        return super(Picking, self).action_confirm()

    def first_validate_action(self, picking):
        products_without_lots = self.env['product.product']

        if self.env.user not in picking.location_id.py_warehouse_id.crm_team_id.member_ids and \
                not self.env.user.has_group('base.group_system') and not self.env.user.has_group('replenishment_internal_transfer.group_validate_sec_first'):
            raise UserError(
                _("Only source location employee can validate this."))

        for line in picking.move_line_ids:
            product = line.product_id
            if product and product.tracking != 'none':
                if not line.lot_name and not line.lot_id:
                    products_without_lots |= product

        if products_without_lots:
            raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))

        picking.flag = False
        picking.state = 'validate2'
        picking.team_f_validate = picking.location_id.py_warehouse_id.crm_team_id
        picking.first_validate_date = fields.Datetime.now()

        # Close all activity on validate
        activities = self.env['mail.activity'].search([('res_id', '=', picking.id)])
        activities.with_user(SUPERUSER_ID).action_done()
        warehouse = picking.location_dest_id.get_warehouse()
        member_ids = warehouse.crm_team_id.member_ids
        dates = []

        for team_user in member_ids:
            data = {
                'res_id': picking.id,
                'res_model_id': self.env.ref('stock.model_stock_picking').id,
                'user_id': team_user.id,
                'summary': 'Validation Arrival Schedule',
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'date_deadline': fields.Date.today(),
            }
            dates.append(data)
        self.env['mail.activity'].create(dates)

    def second_validate_action(self, picking):
        if self.env.user not in picking.location_dest_id.py_warehouse_id.crm_team_id.member_ids and \
                not self.env.user.has_group('base.group_system') and not self.env.user.has_group('replenishment_internal_transfer.group_validate_sec_first')\
                and not picking.location_dest_id.is_expire_location:
            raise UserError(
                _("Only destination location employee can validate this."))

        if self.env.user not in picking.team_f_validate.member_ids or \
                self.env.user.has_group('base.group_system') or  self.env.user.has_group('replenishment_internal_transfer.group_validate_sec_first'):
            result = super(Picking, picking).button_validate()

            if result is True:
                # Close All Activity on picking when second validate
                activities = self.env['mail.activity'].search([('res_id', '=', picking.id)])
                activities.with_user(SUPERUSER_ID).action_done()
            return result
        else:
            raise UserError(
                _("You cannot validate. Please wait for the other employee to approve ."))

    def button_validate(self):
        pickings = self.filtered(
            lambda p: p.picking_type_code == 'internal' and p.location_id.location_id != p.location_dest_id.location_id)

        if not pickings:
            return super(Picking, self).button_validate()

        for picking in pickings:
            if picking.flag:
                # Only from validate first
                self.first_validate_action(picking)
            else:
                # Only from validate Second
                self.second_validate_action(picking)

    def action_assign(self):
        pickings = self.filtered(
            lambda p: p.picking_type_code == 'internal')

        for picking in pickings:
            if self.env.user not in picking.location_id.py_warehouse_id.crm_team_id.member_ids and \
                    not self.env.user.has_group('stock.group_stock_manager'):
                raise UserError(
                    _("Only source location employee can Check Availability."))

        return super(Picking, self).action_assign()

    @api.model_create_multi
    def create(self, values):
        res = super(Picking, self).create(values)

        if res.picking_type_code == 'internal':
            res.partner_id = False
            warehouse = res.location_id.get_warehouse()
            member_ids = warehouse.crm_team_id.member_ids
            dates = []

            for team_user in member_ids:
                data = {
                    'res_id': res.id,
                    'res_model_id': self.env.ref('stock.model_stock_picking').id,
                    'user_id': team_user.id,
                    'summary': 'Product Request Schedule',
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'date_deadline': fields.Date.today(),
                }
                dates.append(data)
            
            self.env['mail.activity'].create(dates)

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    # To prevent reserve qty after first validate
    def _action_assign(self):
        self = self - \
            self.filtered(
                lambda m: m.picking_id and m.picking_id.state == 'validate2')

        super(StockMove, self)._action_assign()

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        pickings = []
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [
                                f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])

        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()

            if picking:
                if any(picking.partner_id.id != m.partner_id.id or
                        picking.origin != m.origin for m in moves):
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })

                # New to add activity when do new assignation
                if picking not in pickings:
                    if picking.picking_type_code == 'internal':
                        warehouse = picking.location_id.get_warehouse()
                        member_ids = warehouse.crm_team_id.member_ids
                        dates = []

                        for team_user in member_ids:
                            data = {
                                'res_id': picking.id,
                                'res_model_id': self.env.ref('stock.model_stock_picking').id,
                                'user_id': team_user.id,
                                'summary': 'Product Request Schedule',
                                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                                'date_deadline': fields.Date.today(),
                            }
                            dates.append(data)
                        
                        self.env['mail.activity'].create(dates)
                    pickings.append(picking)
            else:
                new_picking = True
                picking = Picking.create(moves._get_new_picking_values())

            moves.write({'picking_id': picking.id})
            moves._assign_picking_post_process(new=new_picking)

        return True
