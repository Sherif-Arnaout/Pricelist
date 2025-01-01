from odoo import models
from odoo.exceptions import UserError
from io import BytesIO
import xlsxwriter


class PricelistXlsxReport(models.AbstractModel):
    _name = 'report.pricelist.pricelist_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docs):
        # Add the worksheet
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
        sheet.set_column('B:B', 30)  # Description
        sheet.set_column('C:C', 15)  # Price
        sheet.set_column('D:D', 15)  # Start Date
        sheet.set_column('E:E', 15)  # End Date

        # Write report title
        sheet.merge_range('A1:E1', 'Pricelist Report', title_format)

        # Write pricelist name
        pricelist_name = docs.name or 'N/A'
        sheet.write(1, 0, pricelist_name, title_format)

        # Write header
        headers = ['Product', 'Description', 'Price', 'Start Date', 'End Date']
        for col_num, header in enumerate(headers):
            sheet.write(2, col_num, header, header_format)

        # Write data rows
        row = 3
        for pricelist in docs:
            for item in pricelist.item_ids:
                product_name = item.product_tmpl_id.name or 'N/A'
                description = item.product_tmpl_id.description_sale or 'N/A'
                start_date = item.date_start or 'N/A'
                end_date = item.date_end or 'N/A'

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

                # Write the data
                sheet.write(row, 0, product_name, text_format)
                sheet.write(row, 1, description, text_format)
                sheet.write(row, 2, price, currency_format)
                sheet.write(row, 3, start_date, date_format)
                sheet.write(row, 4, end_date, date_format)
                row += 1
