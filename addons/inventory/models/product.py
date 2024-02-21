from odoo import models, fields, api
import logging

# Configure logger
_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.template'
    
    nom_de_la_structure = fields.Char(string='Name of the Structure')

    uom_po_id = fields.Many2one(string = 'Purchase')
    default_code = fields.Char(string = 'CIP Code')

    partner_id = fields.Many2one('res.partner', string='Partner', compute="compute_supplier_info")

    fabricant = fields.One2many('fabricant', 'product_id', string='Manufacturer')
    
    atc_classe = fields.Many2one('classe.atc', 'ATC Class', group_expand='_read_group_atc_classe')
    
    dci_id = fields.Many2one('dci.name', string='DCI Name')
    
    laboratoire_id = fields.Many2one('laboratoire', string="Laboratory",required=False)
    
    tableau = fields.Selection(selection=[('0', '0'),('1', '1'),('2', '2'),('3', '3'), ('4', '4'), ('5', '5')],string="Table")
    distributeur_id = fields.Many2one('distributeur', string="Distributor")
    gamme_id = fields.Many2one('gamme', string="Gamme")
    couleur_id = fields.Many2one('couleur', string="Color")
    famille_id = fields.Many2one('famille', string="Product family")
                               

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
        string='Products Supplier',
        help="Supplier-related products"
    )

    @api.depends('partner_id')
    def _compute_fournisseur(self):
        for record in self:
            # Recherchez tous les produits ayant le même partenaire (partner_id)
            products_fournisseur = self.env['product.template'].search([('partner_id', '=', record.partner_id.id)])

            # Mettez à jour la liste des produits liés au partenaire
            record.product_fournisseur_ids = products_fournisseur


    # Define the related fields
    quantitys = fields.Float(
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
    def _compute_all_quantities(self):
        for template in self:
            # Gather all positive quantities related to this product template
            positive_quantities = self.env['stock.quant'].search([
                ('product_tmpl_id', '=', template.id),
                ('quantity', '>', 0)  # Only include positive quantities
            ]).mapped('quantity')
            # Concatenate them into a string
            template.all_quantities = ', '.join(map(str, positive_quantities))

    @api.depends('stock_quant_ids.inventory_diff_quantity')
    def _compute_all_inventory_diffs(self):
        for template in self:
            # Gather all inventory diffs (including negative) related to this product template
            inventory_diffs = self.env['stock.quant'].search([
                ('product_tmpl_id', '=', template.id)
            ]).mapped('inventory_diff_quantity')  # Include both positive and negative values
            # Concatenate them into a string
            template.all_inventory_diffs = ', '.join(map(str, inventory_diffs))

    available_qties = fields.Char(string="Avalaible Quantities", compute='_compute_available_quantities' )

    @api.depends('stock_quant_ids.available_quantity')
    def _compute_available_quantities(self):
        for template in self:
            # Gather all available quantites (including negative) related to this product template
            available_qty = self.env['stock.quant'].search([
                ('product_tmpl_id', '=', template.id)
            ]).mapped('available_quantity')  # Include both positive and negative values
            # Concatenate them into a string
            template.available_qties = ', '.join(map(str, available_qty))

    stock_quant_ids = fields.One2many('stock.quant', 'product_tmpl_id', string='Quants') 

    total_qty_received = fields.Float(
        string='Total Quantity Received',
        compute='_compute_total_qty_received',
    )

    #@api.depends('product_variant_ids.purchase_order_line_ids.qty_received')
    def _compute_total_qty_received(self):
        for template in self: 
            total_received = 0.0
            for variant in template.product_variant_ids:
                # Here, we access the implied One2many relationship
                total_received += sum(variant.purchase_order_line_ids.mapped('qty_received'))
            template.total_qty_received = total_received


    quantity = fields.Char(string = "Demand", compute = '_compute_quantity') 
    done = fields.Char(string = "Done", compute ='_compute_done')
    def _compute_quantity(self):
        for product in self:
            stock_data = self.env['stock.move'].search([('product_tmpl_id', '=', product.id)])

            stock_info = ""
            for stock in stock_data: 
                stock_info += f"Demand Quantity: {stock.product_uom_qty}, "

            product.quantity = stock_info

    def _compute_done(self):
        for product in self:
            stock_data = self.env['stock.move'].search([('product_tmpl_id', '=', product.id)])

            stock_info = ""
            for stock in stock_data: 
                stock_info += f"Received Quantity: {stock.quantity_done}, "

            product.done = stock_info

    stock_origin = fields.Char(
        string='Stock Picking Origin',
        compute='_compute_stock_origin',
    )

    @api.depends('product_variant_ids')
    def _compute_stock_origin(self):
        for template in self:
            # Find the most recent stock.picking for any variant of this template
            pickings = self.env['stock.picking'].search([
                ('move_ids.product_id.product_tmpl_id', '=', template.id),
            ], order='date asc')

            # Gather the origins from these pickings
            origins = set(picking.origin for picking in pickings if picking.origin)
            #origins = [picking.origin for picking in pickings if picking.origin]

            # Assign the concatenated origins to the computed field
            template.stock_origin = ', '.join(origins)

    stock_names = fields.Char(
        string='Stock Picking Names',
        compute='_compute_stock_names',
    )

    @api.depends('product_variant_ids')
    def _compute_stock_names(self):
        for template in self:
            # Find all stock.picking records for any variant of this template
            pickings = self.env['stock.picking'].search([
                ('move_ids.product_id.product_tmpl_id', '=', template.id),
            ], order='name asc')

            # Gather unique names from these pickings
            unique_names = set(picking.name for picking in pickings if picking.name)

            # Concatenate unique names into a string
            template.stock_names = ', '.join(unique_names)
    
    stock_dates = fields.Char(string = "Stock date", compute= '_compute_stock_dates')

    @api.depends('product_variant_ids')
    def _compute_stock_dates(self):
        for template in self:
            pickings = self.env['stock.picking'].search([
                ('move_ids.product_id.product_tmpl_id', '=', template.id),
            ], order='date asc')

            # Gather unique names from these pickings
            unique_dates = set(picking.date_done for picking in pickings if picking.date_done)
            #unique_dates = {picking.date_done.date() for picking in pickings if picking.date_done}
            #sorted_dates = sorted(unique_dates)

            # Concatenate unique dates into a string
            #template.stock_dates = ', '.join(unique_dates)
            template.stock_dates = ', '.join(date.strftime(" %m/%d/%Y ") for date in unique_dates)

    partner_ids = fields.Char(string = "Stock Partner", compute= '_compute_partner_ids')

    @api.depends('product_variant_ids')
    def _compute_partner_ids(self):
        for template in self:
            pickings = self.env['stock.picking'].search([
                ('move_ids.product_id.product_tmpl_id', '=', template.id),
            ], order='name asc')

            # Gather unique names from these pickings
            #unique_partners = set(picking.partner_id for picking in pickings if picking.partner_id)
            unique_partners = {picking.partner_id.name for picking in pickings if picking.partner_id}

            # Concatenate unique partners into a string
            template.partner_ids = ', '.join(str(partner_id) for partner_id in unique_partners)

    lot_info = fields.Text(string="Lot Number", compute='_compute_lot_info')
    
    @api.depends('product_variant_ids.stock_ids.name')
    def _compute_lot_info(self):
        for template in self:
            lot_info = []
            # You need to loop through the product variants of the template
            for variant in template.product_variant_ids:
                # Now loop through the lots for each variant
                for lot in variant.stock_ids:
                    info = f"Lot Number: {lot.name}"
                    if lot.expiration_date:
                        info += f", Expiration Date: {fields.Date.to_string(lot.expiration_date)}"
                    lot_info.append(info)
            # Join all the lot information into a single string
            template.lot_info = '\n'.join(lot_info)

    lot_names = fields.Text(string="Lot Names", compute='_compute_lot_names')
    expiration_dates = fields.Text(string="Expiration Date", compute='_compute_expiration_dates')

    @api.depends('product_variant_ids.stock_ids.name')
    def _compute_lot_names(self):
        for template in self:
            lot_names = []
            for variant in template.product_variant_ids:
                for lot in variant.stock_ids:
                    lot_names.append(f"Lot Number: {lot.name}")
            template.lot_names = ', '.join(lot_names)

    #@api.depends('product_variant_ids.stock_ids.expiration_date')
    def _compute_expiration_dates(self):
        for template in self:
            expiration_dates = []
            for variant in template.product_variant_ids:
                for lot in variant.stock_ids:
                    if lot.expiration_date:
                        date_str = fields.Date.to_string(lot.expiration_date)
                        expiration_dates.append(f"Expiration Date: {date_str}")
                        #expiration_dates.append(f"{lot.name}: {date_str}")
            template.expiration_dates = '\n'.join(expiration_dates)

    lot_number = fields.Text(string="Lots/Serial Numbers", compute='_compute_lot_number')
    @api.depends('product_variant_ids.stock_ids.name')
    def _compute_lot_number(self):
        for template in self:
            lot_number = []
            for variant in template.product_variant_ids:
                for lot in variant.stock_ids:
                    lot_number.append(f"Lot Number: • {lot.name}")
            template.lot_number = ', '.join(lot_number)


    lot_prices = fields.Text(string="Cost Price", compute='_compute_lot_prices')
    @api.depends('product_variant_ids.stock_ids.price')
    def _compute_lot_prices(self):
        for template in self:
            lot_prices = []
            for variant in template.product_variant_ids:
                for lot in variant.stock_ids:
                    lot_prices.append(f"Cost Price: • {lot.price}")
            template.lot_prices = ', '.join(lot_prices)

    
    lot_ids = fields.One2many('stock.lot', 'product_lot', string='Lot Prices')
    #compute='_compute_lot_price'

    @api.depends('product_variant_ids.stock_ids')
    def _compute_lot_price(self):
        for template in self:
            lot_prices = []
            for variant in template.product_variant_ids:
                for lot in variant.stock_ids:
                    lot_prices.append((0, 0, {
                        'price': lot.price,
                        'product_lot': template.id,
                    }))
            template.lot_ids = lot_prices
    
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
    name = fields.Char("Manufacturer's Name", required=True)
    description = fields.Char('Description')
    product_id = fields.Many2one('product.template',  string='Products')

class Laboratoire(models.Model):
    _name = 'laboratoire'

    name = fields.Char(string="Name",required=True)
    code = fields.Char(string="Code")
    tel = fields.Char(string=u"Phone Number")
    contact_name = fields.Char(string=u"Responsible's Name")
    
    
class Gamme(models.Model):
    _name = 'gamme'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")

class Couleur(models.Model):
    _name = 'couleur'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")


class Distributeur(models.Model):
    _name = 'distributeur'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")

class Famille(models.Model):
    _name = 'famille'

    name = fields.Char(string="Code", required=True)
    famille = fields.Char(string = "Families")
    description = fields.Char(string = "Description")