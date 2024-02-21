
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DciName(models.Model):
    _name = "dci.name"
    _description = "DCI Name"

    name = fields.Char(string = 'DCI Name', index='trigram', required=True)
    product_id = fields.One2many('product.template', 'dci_id', string = 'Products')
    
    code_atc = fields.Char(string = 'ATC Code')
    dosage = fields.Char(string = 'Dosage')
    forme = fields.Char(string = 'Galenic Form')

    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('categ_id', 'child_of', self.ids)], ['categ_id'], ['categ_id'])
        group_data = dict((data['categ_id'][0], data['categ_id_count']) for data in read_group_res)
        for categ in self:
            product_count = 0
            for sub_categ_id in categ.search([('id', 'child_of', categ.ids)]).ids:
                product_count += group_data.get(sub_categ_id, 0)
            categ.product_count = product_count

