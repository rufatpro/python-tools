import decimal
from typing import List, Union

import openpyxl
from xlsxwriter import Workbook


# https://openpyxl.readthedocs.io/en/stable/tutorial.html
def read_xlsx(book_name):
    wb = openpyxl.load_workbook(book_name)
    ws = wb.active

    data = [[value for value in row] for row in ws.values]
    return data


def print_2_excel_file(excel_file_name: str, data: List, header: Union[List, None] = None, print_group_delim=True,
                       default_column: Union[int, List] = None, freeze_params=None, need_autofilter=False) -> None:
    workbook = Workbook(excel_file_name, {"in_memory": True})

    header_format = workbook.add_format({"bold": True, "align": "center"})
    header_format.set_align('vcenter')

    worksheet = workbook.add_worksheet()

    if default_column:
        if isinstance(default_column, list):
            for row in default_column:
                worksheet.set_column(*row)  # Номер 1 столбца, номер 2-го столбца, ширина диапазона между ними
        elif isinstance(default_column, int):
            worksheet.set_column(1, 100, default_column)  # ширина столбца в character units
        else:
            raise ValueError("Incorrect type of value")

    excel_row_no = 0
    if header is not None:
        for no, txt in enumerate(header):
            worksheet.write(excel_row_no, no, txt, header_format)
        excel_row_no += 1

    format_default = workbook.add_format({})
    format_border = workbook.add_format({"top": 1})
    last_id = ""
    for row in data:

        # Print delimiters between a group of rows, if the first column has an id field.
        tmp_id = str(row[0])
        row_format = format_default if (not print_group_delim) or (last_id == tmp_id) else format_border
        last_id = tmp_id

        for no, txt in enumerate(row):
            write = worksheet.write
            # print(txt, type(txt))
            if isinstance(txt, (int, float, decimal.Decimal)):
                write = worksheet.write_number
            elif txt.startswith(tuple(["https://", "http://", ])):  # noqa
                write = worksheet.write_string
            write(excel_row_no, no, txt, row_format)
        excel_row_no += 1

    if need_autofilter:
        worksheet.autofilter(0, 0, excel_row_no, len(data[0]))

    if freeze_params:
        worksheet.freeze_panes(*freeze_params)  # Фиксированные строки и колонки, freeze row, column

    workbook.close()
