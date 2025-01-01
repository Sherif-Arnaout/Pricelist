from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PriceList(models.Model):
    _inherit = 'product.pricelist'


    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    products = fields.Many2many(
        'product.product',
        string='Products',
        domain=[('active', '=', True)],
        tracking=True
    )

    date_pricelist = fields.Date(string='Date', tracking=True)

    def create_pricelist_items(self):
        for pricelist in self:
            # Check for existing products in pricelist items
            existing_products = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id),
                ('product_tmpl_id', 'in',
                 pricelist.products.mapped('product_tmpl_id').ids)
            ])

            # Collect existing product template IDs
            existing_product_tmpls = existing_products.mapped(
                'product_tmpl_id')

            # Identify products that will cause duplicates
            duplicate_products = existing_product_tmpls

            if duplicate_products:
                # Prepare error message with duplicate product names
                duplicate_names = duplicate_products.mapped('name')
                raise ValidationError(
                    f"The following products already exist in the pricelist: {', '.join(duplicate_names)}")

            # Create pricelist items for unique products
            for product in pricelist.products:
                self.env['product.pricelist.item'].create({
                    'pricelist_id': pricelist.id,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'applied_on': '1_product',
                    'compute_price': 'fixed',
                    'fixed_price': 0
                })


class PriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    ar_description = fields.Text(string='Arabic Description')
    en_description = fields.Text(string='Description')
    sales_description = fields.Text(
        string='Sales Description',
        related='product_tmpl_id.description_sale'
    )
    cost_price = fields.Float(
        string='Cost Price',
        related='product_tmpl_id.standard_price'
    )
    list_price = fields.Float(
        string='List Price',
        related='product_tmpl_id.list_price'
    )
    unit_of_measure = fields.Char(
        string='Unit of Measure',
        related='product_tmpl_id.uom_id.name'
    )
