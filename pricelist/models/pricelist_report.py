from odoo import models, api

class ReportPricelist(models.AbstractModel):
    _name = 'sale.report_pricelist'
    _description = 'Pricelist Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Capture filter parameters from context
        context = self.env.context
        filter_currency = context.get('filter_currency')
        filter_active = context.get('filter_active')
        filter_start_date = context.get('filter_start_date')
        filter_end_date = context.get('filter_end_date')

        # Build domain based on filters
        domain = []
        if filter_currency:
            domain.append(('currency_id', '=', filter_currency.id))
        if filter_active is not None:
            domain.append(('active', '=', filter_active))
        if filter_start_date:
            domain.append(('date_start', '>=', filter_start_date))
        if filter_end_date:
            domain.append(('date_end', '<=', filter_end_date))

        # Get pricelists based on filter criteria
        pricelists = self.env['product.pricelist'].search(domain)

        return {
            'docs': pricelists,
        }
