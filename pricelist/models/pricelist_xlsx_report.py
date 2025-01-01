from odoo import models
from odoo.exceptions import UserError
from io import BytesIO
import xlsxwriter


class PricelistXlsxReport(models.AbstractModel):
    _name = 'report.pricelist.pricelist_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        # Add a worksheet to the workbook
        sheet = workbook.add_worksheet('Pricelist Report')

        # Define formats
        title_format = workbook.add_format(
            {'bold': True, 'font_size': 14, 'align': 'center', 'color': 'red'})
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'color': 'green'})
        text_format = workbook.add_format({'align': 'left'})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Adjust column widths
        sheet.set_column('A:A', 20)  # Product
        sheet.set_column('B:B', 30)  # Sales Description
        sheet.set_column('C:C', 12)  # Price
        sheet.set_column('D:D', 20)  # Start Date
        sheet.set_column('E:E', 20)  # End Date
        sheet.set_column('F:F', 30)  # Arabic Description
        sheet.set_column('G:G', 30)  # English Description
        sheet.set_column('H:H', 12)  # Cost Price
        sheet.set_column('I:I', 12)  # List Price
        sheet.set_column('J:J', 10)  # Unit of Measure

        # Write report title
        sheet.merge_range('A1:E1', 'Pricelist Report', title_format)

        # Define headers
        headers = [
            'Product', 'Sales Description', 'Price', 'Start Date', 'End Date',
            'Arabic Description', 'English Description', 'Cost Price', 'List Price', 'Unit of Measure'
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header, header_format)

        # Write data rows
        row = 3
        for item in wizard.filtered_items:
            # Calculate the price based on the compute_price method
            if item.compute_price == 'fixed':
                price = item.fixed_price or 0.0
            elif item.compute_price == 'percentage':
                price = item.product_tmpl_id.list_price - (
                    (item.percent_price * item.product_tmpl_id.list_price) / 100)
            elif item.compute_price == 'formula' and item.base == 'list_price':
                price = item.product_tmpl_id.list_price - (
                    (item.price_discount * item.product_tmpl_id.list_price) / 100) + item.price_surcharge
            elif item.compute_price == 'formula' and item.base == 'standard_price':
                price = item.product_tmpl_id.standard_price - (
                    (item.price_discount * item.product_tmpl_id.standard_price) / 100) + item.price_surcharge
            else:
                price = 0.0

            # Write row data in the specified order
            sheet.write(row, 0, item.product_tmpl_id.name, text_format)  # Product
            sheet.write(row, 1, item.product_tmpl_id.description_sale if wizard.show_sales_description else '', text_format)  # Sales Description
            sheet.write(row, 2, price, currency_format)  # Price
            sheet.write(row, 3, item.date_start if wizard.date_start else '', date_format)  # Start Date
            sheet.write(row, 4, item.date_end if wizard.date_end else '', date_format)  # End Date
            sheet.write(row, 5, item.ar_description if wizard.show_ar_description else '', text_format)  # Arabic Description
            sheet.write(row, 6, item.en_description if wizard.show_en_description else '', text_format)  # English Description
            sheet.write(row, 7, item.product_tmpl_id.standard_price if wizard.show_cost_price else '', currency_format)  # Cost Price
            sheet.write(row, 8, item.product_tmpl_id.list_price if wizard.show_list_price else '', currency_format)  # List Price
            sheet.write(row, 9, item.product_tmpl_id.uom_id.name if wizard.show_unit_of_measure else '', text_format)  # Unit of Measure
            row += 1