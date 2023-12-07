from odoo import models, fields, api,_
from odoo.exceptions import UserError


class MailActivity(models.Model):
    _inherit = "mail.activity"
    
    def write(self, values):
        if "user_id" in values and not self.env.user.has_group('base.group_system'): 
            raise UserError(_('You can\'t change activity user.'))

        result = super().write(values)
    
        return result
    
    def unlink(self):
        if self.user_id and self.env.user != self.user_id\
            and not self.env.user.has_group('stock.group_stock_manager'):
            raise UserError(_('You can only set your activity to done.'))
        elif self.user_id and self.env.user == self.user_id\
            and self.res_model_id.model == 'stock.picking'\
            and not self.env.user.has_group('stock.group_stock_manager'):

            stock_picking = self.env['stock.picking'].browse(self.res_id)

            if stock_picking and stock_picking.state == 'draft' and \
                self.env.user in stock_picking.location_dest_id.py_warehouse_id.crm_team_id.member_ids:
                raise UserError(_('Please Mark Transfer As ToDo.'))
            elif stock_picking and stock_picking.state in ('waiting','confirmed','assigned') and \
                self.env.user in stock_picking.location_id.py_warehouse_id.crm_team_id.member_ids:
                raise UserError(_('Please Validate Transfer.'))
            elif stock_picking and stock_picking.state == 'validate2' and \
                self.env.user in stock_picking.location_dest_id.py_warehouse_id.crm_team_id.member_ids:
                raise UserError(_('Please Validate2 Transfer.'))
        
        result = super().unlink()
    
        return result
    

    