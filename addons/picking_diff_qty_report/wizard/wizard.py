from odoo import models, fields


class WizardReportExcel(models.TransientModel):
    _name = 'wizard.report.excel'
    _description = 'Wizard Report Excel'
  
    attachment_ids = fields.Many2many('ir.attachment', string='Files')