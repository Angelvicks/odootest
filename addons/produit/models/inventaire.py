from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    dci_ids = fields.Many2one('dci', string='DCI')


class DCI(models.Model):
    _name = "dci"
    
    name =fields.Char('name',required=True)
    code_dci = fields.Integer('Code DCI')
    description = fields.Char('Description')
    product_ids = fields.One2many('product.template', 'dci_ids', string='Produits')