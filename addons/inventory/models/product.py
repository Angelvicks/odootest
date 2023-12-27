from odoo import models, fields, api


class product(models.Model):
   _inherit = 'product.template'

  # _inherit = 'product.product'
   
   aire_sante = fields.Char(string='Aire de santé')
   region = fields.Char(string='Région')
   district_sante = fields.Char(string='District de santé')
   num_PVR = fields.Float(string='N°PVR')
   num_bc = fields.Char(string='N°BC')
   num_bl = fields.Char(string='N°BL')
   nom_de_la_structure = fields.Char(string='Nom de la Structure')
   nom_DCI = fields.Char(string='Nom (DCI)')
   uom_po_id = fields.Many2one(string = 'Purchase')

   