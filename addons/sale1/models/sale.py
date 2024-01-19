from odoo import api, fields, models


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    order_line = fields.One2many('sale.order.line', 'order_id')
    
    @api.depends('order_line')
    def _compute_alternative_products(self):
        for order in self:
            produit_ids = []
            for line in order.order_line:
                product_tmp = line.product_id.product_tmpl_id
                dci = product_tmp.dci_id
                if dci:
                    dci1 = self.env['dci'].search([('id', '=', dci.id)])
                    produit_ids += dci1.product_ids.ids
            order.alternative_products = self.env['product.template'].browse(produit_ids)

    alternative_products = fields.One2many('product.template', compute='_compute_alternative_products')
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def alternative(self):
        produit_ids = []
        for line in self:
            product_tmp = line.product_id.product_tmpl_id
            dci = product_tmp.dci_id
            if dci:
                dci1 = self.env['dci'].search([('id', '=', dci.id)])
                produit_ids += dci1.product_ids.ids
        return self.env['product.template'].browse(produit_ids)
        
       
            
            