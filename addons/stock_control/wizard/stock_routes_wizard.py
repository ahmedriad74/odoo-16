from odoo import fields, models, api, _


class StockRoutesWizard(models.TransientModel):
    _name = 'stock.routes.wizard'
    _description = 'Stock Routes Wizard'

    order_point_id = fields.Many2one(
        string='Order Point',
        comodel_name='stock.warehouse.orderpoint'
    )
    route_line_ids = fields.One2many('stock.routes.line.wizard', 'wiz_id')
    message = fields.Text('Message', required=True)
    qty_to_order = fields.Float(string='QTY To Order')
    edit_qty = fields.Boolean(string='Edit QTY')

    def action_create(self):
        current_order = self.order_point_id

        for route in self.route_line_ids:
            if route.to_order > 0:
                new_line = current_order.copy()

                new_line.write({
                    'route_id': route.route_id.id,
                    'branch_order_qty': route.to_order
                })

        if sum(self.route_line_ids.mapped('to_order')) > 0:
            current_order.unlink()

        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('route_line_ids')
    def _onchange_sequence(self):
        qty_to_order = self.qty_to_order
        route_line_ids = self.route_line_ids.sorted(lambda line: line.sequence)
        
        if not self.edit_qty:
            for line in route_line_ids:
                if qty_to_order > 0:
                    if line.available >= qty_to_order:
                        to_order = qty_to_order
                    else:
                        to_order = line.available

                    qty_to_order = qty_to_order - to_order

                    if line.route_id.py_is_buy_route:
                        to_order = qty_to_order
                        qty_to_order = 0
                else:
                    to_order = 0
                
                line.to_order = to_order
            
    
class StockRoutesLineWizard(models.TransientModel):
    _name = 'stock.routes.line.wizard'
    _description = 'Stock Routes Wizard'
    _order = 'sequence'

    wiz_id = fields.Many2one('stock.routes.wizard')
    route_id = fields.Many2one('stock.route')
    available = fields.Float()
    to_order = fields.Float()
    sequence = fields.Integer('Sequence', default=0)