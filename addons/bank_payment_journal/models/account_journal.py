from odoo import api, fields, models, _

class account_journal(models.Model):
    _inherit = "account.journal"
     
    bank_charges_account_id = fields.Many2one('account.account',string='Bank Charges Account')
    charge_percentage = fields.Float(string=u'Charge Percentage (%)')
    
    @api.onchange('type')
    def _onchange_field_type(self):
        if self.type != 'bank':
            self.bank_charges_account_id = False
            self.charge_percentage = 0
    
    