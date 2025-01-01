from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PricelistReportWizard(models.TransientModel):
    _name = 'pricelist.report.wizard'
    _description = 'Pricelist Report Wizard'

    # Fields
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', required=True, domain=[('active', '=', True)])
    show_ar_description = fields.Boolean(
        string='Arabic Description', default=False)
    show_en_description = fields.Boolean(
        string='English Description', default=False)
    show_sales_description = fields.Boolean(
        string='Sales Description', default=False)
    show_cost_price = fields.Boolean(string='Cost Price', default=False)
    show_list_price = fields.Boolean(string='List Price', default=False)
    show_unit_of_measure = fields.Boolean(
        string='Unit of Measure', default=False)

    product_category_id = fields.Many2one(
        'product.category', string='Product Category')
    min_price = fields.Float(string='Minimum Price')
    max_price = fields.Float(string='Maximum Price')
    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date')

    filtered_items = fields.One2many(
        comodel_name='product.pricelist.item',  # Model of the related records
        compute='_compute_filtered_items',
        string='Filtered Items',
    )

    @api.constrains('min_price', 'max_price')
    def _check_price_range(self):
        for wizard in self:
            if wizard.min_price and wizard.max_price and wizard.min_price > wizard.max_price:
                raise ValidationError(
                    "Minimum price cannot be greater than maximum price.")

    @api.depends('pricelist_id', 'product_category_id', 'min_price', 'max_price')
    def _compute_filtered_items(self):
        """Applies the filters to pricelist items and assigns them to the computed field."""
        for wizard in self:
            items = wizard.pricelist_id.item_ids

            # Apply category filter
            if wizard.product_category_id:
                items = items.filtered(
                    lambda i: i.product_tmpl_id.categ_id == wizard.product_category_id)

            # Apply price filters
            if wizard.min_price:
                items = items.filtered(
                    lambda i: i.fixed_price >= wizard.min_price)
            if wizard.max_price:
                items = items.filtered(
                    lambda i: i.fixed_price <= wizard.max_price)

            # Apply date filters
            if wizard.date_start:
                items = items.filtered(
                    lambda i: i.date_start >= wizard.date_start)
            if wizard.date_end:
                items = items.filtered(lambda i: i.date_end <= wizard.date_end)

            # Assign the filtered items
            wizard.filtered_items = items

    def _get_report_values(self, docids, data=None):
        docs = self.env['pricelist.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pricelist.report.wizard',
            'docs': docs,
            'filtered_items': docs.filtered_items,
        }

    def print_report(self):
        if not self.filtered_items:
           raise ValidationError("No items match the selected filters.")
        return self.env.ref('pricelist.action_report_pricelist_wizard').report_action(self)


    def print_report_wizard(self):
        if not self.filtered_items:
           raise ValidationError("No items match the selected filters.")
        return self.env.ref('pricelist.action_pricelist_xlsx_report').report_action(self)
    
    def clear_filters(self):
        self.write({
           'product_category_id': False,
           'min_price': 0,
           'max_price': 0,
           'date_start': False,
           'date_end': False,
        })
        # Return an action to reload the wizard
        return {
           'type': 'ir.actions.act_window',
           'res_model': self._name,
           'res_id': self.id,
           'view_mode': 'form',
           'target': 'new',
        }

    def action_preview(self):
        if not self.filtered_items:
           raise ValidationError("No items match the selected filters.")
        return {
           'type': 'ir.actions.act_window',
           'name': 'Preview Filtered Items',
           'res_model': 'product.pricelist.item',
           'view_mode': 'tree,form',
           'domain': [('id', 'in', self.filtered_items.ids)],
           'target': 'new',}
