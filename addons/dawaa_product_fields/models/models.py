# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    
    name = fields.Char('Name',required=True)

    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductModel(models.Model):
    _name = 'product.levela'
    _description = 'Product Level A'
    
    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductColor(models.Model):
    _name = 'product.levelb'
    _description = 'Product Level B'
    
    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductSize(models.Model):
    _name = 'product.levelc'
    _description = 'Product Level C'
    
    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductInvNo(models.Model):
    _name = 'product.leveld'
    _description = 'Product Level D'
    
    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductGender(models.Model):
    _name = 'product.levele'
    _description = 'prdocut Level E'

    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]


class ProductMaterial(models.Model):
    _name = 'product.levelf'
    _description = 'Product Level F'
    
    name = fields.Char('Name',required=True)
    ro_target = fields.Boolean('Target')
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductType(models.Model):
    _name = 'product.item.company'
    _description = 'Product Item Company'
    
    name = fields.Char('Name',required=True)
    
    _sql_constraints = [
        ('nameUniq', 'unique(name)', 'Name already exist!'),
    ]

class ProductProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one(
        string='Brand',
        comodel_name='product.brand'
    )
    levela_id = fields.Many2one(
        string='LevelA',
        comodel_name='product.levela'
    )
    levelb_id = fields.Many2one(
        string='LevelB',
        comodel_name='product.levelb'
    )
    levelc_id = fields.Many2one(
        string='LevelC',
        comodel_name='product.levelc'
    )
    leveld_id = fields.Many2one(
        string='LevelD',
        comodel_name='product.leveld'
    )
    levele_id = fields.Many2one(
        string='LevelE',
        comodel_name='product.levele'
    )
    levelf_id = fields.Many2one(
        string='LevelF',
        comodel_name='product.levelf'
    ) 
    item_comapny_id = fields.Many2one(
        string='Item Company',
        comodel_name='product.item.company'
    )
    vendor_id = fields.Many2one('res.partner', "Vendor")
