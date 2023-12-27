from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    aire_sante = fields.Char(string='Aire de santé')
    region = fields.Char(string='Région')
    district_sante = fields.Char(string='District de santé')
    num_PVR = fields.Float(string='N°PVR')
    num_bc = fields.Char(string='N°BC')
    num_bl = fields.Char(string='N°BL')
    nom_de_la_structure = fields.Char(string='Nom de la Structure')
    nom_DCI = fields.Char(string='Nom (DCI)')
    uom_po_id = fields.Many2one('product.uom', string='Purchase UOM')
    partner_id = fields.Many2one('res.partner', string='Partner', compute="compute_supplier_info")
    #date = fields.Date(string='Date', compute="compute_date")

    def compute_supplier_info(self):
        for record in self:
            supplier_infos = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', record.id)])
            if supplier_infos:
                record.partner_id = supplier_infos[0].partner_id
            else:
                record.partner_id = False
           

                  



   