# -*- coding: utf-8 -*-

from lxml import etree
from odoo import api, fields, models, _

# upgdrade16
class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.distribution.model'
    
    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )
# 

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    product_category_id = fields.Many2one(
        string='Product Category',
        comodel_name='product.category'
    )
    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )

    _sql_constraints = [
        ('crmTeamIdUniq', 'unique(product_category_id, crm_team_id)',
         'Team and Category is in another analytic account!'),
    ]

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    crm_team_id = fields.Many2one(
        string='CRM Team',
        comodel_name='crm.team'
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # upgrade16 ==> 'analytic_account_id' --> 'analytic_distribution'
    # def _prepare_invoice_line(self, **optional_values):
    #     res = super()._prepare_invoice_line(**optional_values)
    #     if self.order_id.team_id and self.product_id.categ_id:
    #         account_analytic_id = self.env['account.analytic.account'].search(
    #             [('product_category_id', '=', self.product_id.categ_id.id), ('crm_team_id', '=', self.order_id.team_id.id)])
    #         if len(account_analytic_id) == 0:
    #             account_analytic_id = self.env['account.analytic.account'].search(
    #                 [('product_category_id', '=', self.product_id.categ_id.parent_id.id), ('crm_team_id', '=', self.order_id.team_id.id)])
    #         res['analytic_account_id'] = account_analytic_id
    #     return res

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        domain = [('crm_team_id', '=', self.order_id.team_id.id)]
        account_analytic_ids = self.env['account.analytic.account'].search(domain)

        if self.order_id.team_id and self.product_id.categ_id:
            account_analytic_id = account_analytic_ids.filtered(lambda acc: acc.product_category_id == self.product_id.categ_id.id)
            if len(account_analytic_id) == 0:
                account_analytic_id = account_analytic_ids.filtered(lambda acc: acc.product_category_id == self.product_id.categ_id.parent_id.id)
            
            if account_analytic_id:
                res['analytic_distribution'] = str(account_analytic_id.id)
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('team_id')
    def _onchange_field_team(self):
        if self.team_id:
            warehouse = self.env['stock.warehouse'].search([('crm_team_id', '=', self.team_id.id)], limit=1)
            if warehouse:
                self.warehouse_id = warehouse

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super(PurchaseOrderLine, self)._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po)

        # add analytic line based on product category and sales team
        analytic_account = self._get_analytic_account(po, product_id)
        if analytic_account:
            res['account_analytic_id'] = analytic_account

        return res

    def _get_analytic_account(self, po, product_id):
        result = False
        so = po._get_sale_orders().ids
        if so:
            account_analytic_id = self.env['account.analytic.account'].search([
                ('product_category_id', '=', product_id.categ_id.id), ('crm_team_id', '=', so[0].team_id.id)])
            if account_analytic_id:
                result = account_analytic_id.id
        return result

class AccountPayment(models.TransientModel):
    _inherit = "account.payment.register"

    team_id = fields.Many2one(
        string='Team',
        comodel_name='crm.team'
    )
    journal_id = fields.Many2one('account.journal')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        team_id = self._context.get('team_sales')
        if team_id:
            res['team_id'] = team_id
        else:
            res['team_id'] = False
        return res

    # upgrade16
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form',
    #                     toolbar=False, submenu=False):

    #     res = super(AccountPayment, self).fields_view_get(
    #         view_id=view_id, view_type=view_type,
    #         toolbar=toolbar, submenu=submenu)

    #     doc = etree.XML(res['arch'])
    #     nodes = doc.xpath("//field[@name='journal_id']")

    #     if not self.env.user.has_group('base.group_system'):
    #         for node in nodes:
    #             node.set('domain', "[('crm_team_id', '=', team_id), ('company_id','=', company_id),('type', 'in', ('bank', 'cash'))]")
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

    @api.depends('payment_type')
    def _compute_available_journal_ids(self):
        """
        Get all journals having at least one payment method for inbound/outbound depending on the payment_type.
        """
        if self.env.user.has_group('base.group_system'):
            journals = self.env['account.journal'].search([
                ('company_id', 'in', self.company_id.ids), ('type', 'in', ('bank', 'cash'))
            ])
        else:
            journals = self.env['account.journal'].search([
                ('company_id', 'in', self.company_id.ids), ('type', 'in', ('bank', 'cash'), ('crm_team_id', '=', self.team_id.id))
            ])
        return super(AccountPayment, self)._compute_available_journal_ids()

    # upgrade16
    # @api.depends('can_edit_wizard', 'company_id')
    # def _compute_journal_id(self):
    #     super(AccountPayment, self)._compute_journal_id()
    #     for wizard in self:
    #         if wizard.team_id:
    #             wizard.journal_id = self.env['account.journal'].search(
    #                 [('crm_team_id', '=', wizard.team_id.id), ('type', 'in', ['bank', 'cash']),
    #                     ('company_id', '=', wizard.company_id.id)], limit=1)

    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        super(AccountPayment, self)._compute_journal_id()
        for wizard in self:
            if wizard.team_id:
                wizard.journal_id = self.env['account.journal'].search([
                    ('crm_team_id', '=', wizard.team_id.id),
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                    ('id', 'in', self.available_journal_ids.ids)
                ], limit=1)

class AccountInvoice(models.Model):
    _inherit = "account.move"

    order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        compute='_compute_sale_order',
        store=True
    )

    @api.depends('invoice_origin')
    def _compute_sale_order(self):
        for move in self:
            sale_order = self.env['sale.order'].search(
                [('name', '=', move.invoice_origin)])
            if sale_order:
                move.order_id = sale_order
            else:
                move.order_id = False

class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    # upgrade16
    @api.depends('account_id', 'partner_id', 'product_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if line.display_type == 'product' or not line.move_id.is_invoice(include_receipts=True):
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    'crm_team_id': self.move_id.team_id.id,
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.partner_id.id,
                    "partner_category_id": line.partner_id.category_id.ids,
                    "account_prefix": line.account_id.code,
                    "company_id": line.company_id.id,
                })
                # override
                line.analytic_distribution = distribution or False
                # 
    # upgrade16
    @api.onchange('product_id')
    def _onchange_product(self):
        self._compute_analytic_distribution()