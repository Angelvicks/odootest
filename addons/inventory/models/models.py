# -*- coding: utf-8 -*-

from odoo import models, fields, api


class inventory(models.Model):
   #_inherit = 'product.template'

   _inherit = 'product.product'

   default_code = fields.Char(string = 'CIP Code')
   nom_de_la_structure = fields.Char(string='Name of the Structure')
   fabricant = fields.One2many('fabricant', 'product_id', string = 'Manufacturer')
    
   atc_classe = fields.Many2one('classe.atc', 'ATC Class', group_expand='_read_group_atc_classe')
    
   dci_id = fields.Many2one('dci.name', string = 'DCI Name')
    
   laboratoire_id = fields.Many2one('laboratoire', string="Laboratory",required=False)
    
   tableau = fields.Selection(selection=[('0', '0'),('1', '1'),('2', '2'),('3', '3'), ('4', '4'), ('5', '5')],string="Table")
   distributeur_id = fields.Many2one('distributeur', string="Distributor")
   gamme_id = fields.Many2one('gamme', string="Gamme")
   couleur_id = fields.Many2one('couleur', string="Color")
   famille_id = fields.Many2one('famille', string="Product family")

   

   stock_ids = fields.One2many('stock.lot', 'product_id', string='Stock Lots')
   purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        relation='product_purchase_order_rel',  # Name of the relationship table
        column1='product_id',
        column2='purchase_order_id',
        string='Purchase Orders'
    )
   
   stock_picking = fields.One2many('stock.picking', 'product_id', string = 'Stock Picking')

class stock(models.Model):
    _inherit = 'stock.lot'

    #ref = fields.Char(string = 'CIP Code')
    price = fields.Float(string = 'Cost Price')
    product_lot = fields.Many2one('product.template', string='Product Template')
   

  # _name = 'inventory.inventory'
  # _description = 'inventory.inventory'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
