from odoo.tests.common import TransactionCase

class DciName(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(DciName, self).setUp(*args, **kwargs)
        # Creating a product category for use in tests
        self.product_category = self.env['product.category'].create({
            'name': 'Test Category',
        })
        # Creating a DCI Name record for tests
        self.dci_name = self.env['dci.name'].create({
            'name': 'Test DCI',
            'code_atc': 'Test ATC Code',
            'dosage': 'Test Dosage',
            'forme': 'Test Form',
        })
        # Creating product.template records related to the DCI Name
        self.product_1 = self.env['product.template'].create({
            'name': 'Test Product 1',
            'categ_id': self.product_category.id,
            'dci_id': self.dci_name.id,
        })
        self.product_2 = self.env['product.template'].create({
            'name': 'Test Product 2',
            'categ_id': self.product_category.id,
            'dci_id': self.dci_name.id,
        })

    def test_compute_product_count(self):
        """Test the _compute_product_count method."""
        # Trigger the compute method directly
        self.dci_name._compute_product_count()
        
        # Check if the computed count matches the expected number of products
        self.assertEqual(self.dci_name.product_count, 2, "The product count should be 2.")
