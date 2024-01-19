from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    aire_sante = fields.Char(string='Aire de santé')
    region = fields.Char(string='Région')
    district_sante = fields.Char(string='District de santé')
    num_PVR = fields.Integer(string='N°PVR')
    num_bc = fields.Char(string='N°BC')
    num_bl = fields.Char(string='N°BL')
    nom_de_la_structure = fields.Char(string='Nom de la Structure')

    #nom_dci = fields.Char(string='Nom (DCI)')

    uom_po_id = fields.Many2one(string = 'Purchase')

    partner_id = fields.Many2one('res.partner', string='Partner', compute="compute_supplier_info")

    code_cip = fields.Integer(string = 'Code CIP')
    fabricant = fields.One2many('fabricant', 'product_id', string = 'Fabricant')

    #classe_id = fields.One2many('classe_atc', 'product_id', string = 'Classe ATC')
    atc_classe = fields.Many2one('classe.atc', 'Classe ATC', group_expand='_read_group_atc_classe')
    
    dci_id = fields.Many2one('dci.name', string = 'DCI Name')
    famille = fields.Selection([('DIVERS','DIVERS'),('PRODUITS PARA PHARMACEUTIQUES','PRODUITS PARA PHARMACEUTIQUES'),
                                ('PRODUITS PHARMACEUTIQUES', 'PRODUITS PHARMACEUTIQUES'),
                                ('PRODUITS COSMETIQUES', 'PRODUITS COSMETIQUES'),('psychotrope', 'PRODUITS PSYCHOTROPES')], string="Famille")
    laboratoire_id = fields.Many2one('laboratoire', string="Laboratoire",required=False)
    contingente = fields.Boolean(string=u"Contingenté")
    tableau = fields.Selection(selection=[('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],string="Tableau")
    distributeur_id = fields.Many2one('distributeur', string="Distributeur")
    gamme_id = fields.Many2one('gamme', string="Gamme")
    couleur_id = fields.Many2one('couleur', string="Couleur")
    famille_id = fields.Many2one('famille', string="Famille du Produit")
                               

    #dci_id = fields.Many2one('dci', string='DCI')

    def _read_group_atc_classe(self, categories, domain, order):
        category_ids = self.env.context.get('default_atc_classe')
        if not category_ids and self.env.context.get('group_expand'):
            category_ids = categories._search([], order=order)
        return categories.browse(category_ids)

    def compute_supplier_info(self):
        for record in self:
            supplier_infos = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', record.id)])
            if supplier_infos:
                #record.partner_id = supplier_info.partner_id
                record.partner_id = supplier_infos[0].partner_id
            else:
                record.partner_id = False
    
    product_fournisseur_ids = fields.Many2many(
        comodel_name='product.template',
        relation='product_supplier_rel',
        column1='product_id',
        column2='supplier_id',
        string='Produits Fournisseur',
        help="Produits liés au fournisseur"
    )

    @api.depends('partner_id')
    def _compute_fournisseur(self):
        for record in self:
            # Recherchez tous les produits ayant le même partenaire (partner_id)
            products_fournisseur = self.env['product.template'].search([('partner_id', '=', record.partner_id.id)])

            # Mettez à jour la liste des produits liés au partenaire
            record.product_fournisseur_ids = products_fournisseur


    # Define the related fields
    quantity = fields.Float(
        string='Quantity',
        related='stock_quant_ids.quantity',
        readonly=True
    )
    inventory_diff = fields.Float(
        string='Inventory Difference',
        related='stock_quant_ids.inventory_diff_quantity',
        readonly=True
    )

    # Computed field to store concatenated quantity values
    all_quantities = fields.Char(
        string='All Quantities',
        compute='_compute_all_quantities'
    )

    # Computed field to store concatenated inventory difference values
    all_inventory_diffs = fields.Char(
        string='All Inventory Differences',
        compute='_compute_all_inventory_diffs'
    )

    @api.depends('stock_quant_ids.quantity')
    def _compute_all_quantity(self):
        for template in self:
            quantities = template.stock_quant_ids.mapped('quantity')
            template.all_quantities = ', '.join(map(str, quantities))

    @api.depends('stock_quant_ids.inventory_diff_quantity')
    def _compute_all_inventory_diff(self):
        for template in self:
            inventory_diffs = template.stock_quant_ids.mapped('inventory_diff_quantity')
            template.all_inventory_diffs = ', '.join(map(str, inventory_diffs))

    @api.depends('stock_quant_ids.quantity')
    def _compute_all_quantities(self):
        for template in self:
            # Gather all quantities related to this product template
            quantities = self.env['stock.quant'].search([
                ('product_tmpl_id', '=', template.id)
            ]).mapped('quantity')
            # Concatenate them into a string
            template.all_quantities = ', '.join(map(str, quantities))

    @api.depends('stock_quant_ids.inventory_diff_quantity')
    def _compute_all_inventory_diffs(self):
        for template in self:
            # Gather all inventory diffs related to this product template
            inventory_diffs = self.env['stock.quant'].search([
                ('product_tmpl_id', '=', template.id)
            ]).mapped('inventory_diff_quantity')  # Ensure 'inventory_diff' field exists
            # Concatenate them into a string
            template.all_inventory_diffs = ', '.join(map(str, inventory_diffs))

        query = """ select id , product_id, quantity, inventory_quantity, inventory_diff_quantity from stock_quant """
        self.env.cr.execute(query)
        stock = self.env.cr.dictfetchone()
        print("Stock Values: -----> ", stock)

    def _compute_stock_id(self):
        # Fetch data from stock.lot model and build the desired information
        for product in self:
            # Query the stock.lot model for relevant data
            stock_data = self.env['stock.quant'].search([('product_tmpl_id', '=', product.id)])

            # Build the lot information string (you can customize this)
            stock_info = ""
            for stock in stock_data:
                stock_info += f"Stock Number: {stock.inventory_diff_quantity}, Stock Quantity: {stock.quantity}, ..."
            
            product.stock_id = stock_info

    stock_quant_ids = fields.One2many('stock.quant', 'product_tmpl_id', string='Quants')   
    stock_id = fields.Char(string="Quantity", compute='_compute_stock_id')


    lot_id = fields.Char(string="Lot Number", compute='_compute_lot_id')
    expiration_date = fields.Char(string="Expiration Date", compute='_compute_date')

    #@api.depends('your_field')  # Add relevant dependencies
    def _compute_lot_id(self):
        # Fetch data from stock.lot model and build the desired information
        for product in self:
            # Query the stock.lot model for relevant data
            lot_data = self.env['stock.lot'].search([('product_id', '=', product.id)])

            # Build the lot information string (you can customize this)
            lot_info = ""
            for lot in lot_data:
                lot_info += f"Lot Number: {lot.name}, ..."
            
            product.lot_id = lot_info
    
    def _compute_date(self):
        for product in self:
            lot_data = self.env['stock.lot'].search([('product_id', '=', product.id)])

            # Build the lot information string (you can customize this)
            lot_date = ""
            for lot in lot_data:
                lot_date += f"Date: {lot.expiration_date}, ..."
            
            product.expiration_date = lot_date


    
      # Assuming this is the relational field connecting to product.packaging
    packaging_ids = fields.One2many('product.packaging', 'product_id', string='Packaging')

    # Computed field to store packaging names
    packaging_names = fields.Text(compute='_compute_packaging_names')

    @api.depends('packaging_ids')
    def _compute_packaging_names(self):
        """
        Compute and store the names of the packaging from related product.packaging records.
        """
        for record in self:
            # This line fetches the names from the related product.packaging records
            packaging_names = ", ".join(packaging.name for packaging in record.packaging_ids)
            record.packaging_names = packaging_names


class Fabricant(models.Model):
    _name = "fabricant"
    
    #name =fields.Char('Name',required=True)
    name = fields.Char('Nom du Fabricant', required=True)
    description = fields.Char('Description')
    product_id = fields.Many2one('product.template',  string='Produits')

class Laboratoire(models.Model):
    _name = 'laboratoire'

    name = fields.Char(string="Nom",required=True)
    code = fields.Char(string="Code")
    tel = fields.Char(string=u"Téléphone")
    contact_name = fields.Char(string=u"Nom responsable")
    
    
class Gamme(models.Model):
    _name = 'gamme'

    name = fields.Char(string="Nom", required=True)
    code = fields.Char(string="Code")

class Couleur(models.Model):
    _name = 'couleur'

    name = fields.Char(string="Nom", required=True)
    code = fields.Char(string="Code")


class Distributeur(models.Model):
    _name = 'distributeur'

    name = fields.Char(string="Nom", required=True)
    code = fields.Char(string="Code")

class Famille(models.Model):
    _name = 'famille'

    name = fields.Char(string="Code", required=True)
    famille = fields.Char(string = "Familles")
    description = fields.Char(string = "Description")