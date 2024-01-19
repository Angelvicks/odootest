# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ClasseATC(models.Model):
    _name = "classe.atc"
    _description = "Classe ATC"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index='trigram', required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    code_atc = fields.Char( string = 'Code ATC', index=True, required=True)
    parent_id = fields.Many2one('classe.atc', 'Parent Classe ATC', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many('classe.atc', 'parent_id', 'Child Classes')
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this category (Does not consider the children categories)")

    @api.depends('name', 'parent_id.complete_name', 'code_atc')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / (%s) %s' % (category.parent_id.complete_name, category.code_atc, category.name)
            else:
                category.complete_name = '(%s) %s' % (category.code_atc, category.name)

    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('atc_classe', 'child_of', self.ids)], ['atc_classe'], ['atc_classe'])
        group_data = dict((data['atc_classe'][0], data['atc_classe_count']) for data in read_group_res)
        for categ in self:
            product_count = 0
            for sub_atc_classe in categ.search([('id', 'child_of', categ.ids)]).ids:
                product_count += group_data.get(sub_atc_classe, 0)
            categ.product_count = product_count

    @api.constrains('parent_id', 'code_atc')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive classe ATC.'))

    @api.model
    def name_create(self, code_atc, name):
        return self.create({'code_atc': code_atc,'name': name}).name_get()[0]

    def name_get(self):
            if not self.env.context.get('hierarchical_naming', True):
                return [(record.id, record.name, '(' + str(record.code_atc) + ')') for record in self]
            return super().name_get()
