# -*- coding: utf-8 -*-

from odoo import models, fields, api


class inventory(models.Model):
   #_inherit = 'product.template'

   _inherit = 'product.product'

   date_de_reception = fields.Date(String="Date de recepetion" , required = True)
   numero_de_lot = fields.Char(String="Numéro de Lot" , required = True)
   conditionement = fields.Char(String = "Conditionement", required=True)
   dosage = fields.Char(String = "Dosage", required=True)
   fournisseur = fields.Char(String = "fournisseur", required=True)

   aire_sante = fields.Char(string='Aire de santé')
   region = fields.Char(string='Région')
   district_sante = fields.Char(string='District de santé')
   
   num_PVR = fields.Float(string='N°PVR')
   num_bc = fields.Char(string='N°BC')
   num_bl = fields.Char(string='N°BL')
   nom_de_la_structure = fields.Char(string='Nom de la Structure')
   nom_DCI = fields.Char(string='Nom (DCI)')

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
