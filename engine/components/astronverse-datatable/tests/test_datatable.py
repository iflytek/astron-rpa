from unittest import TestCase

from astronverse.datatable import (
    AppendShift,
    CellInsertShift,
    ColumnInsertShift,
    ConditionType,
    CopyType,
    DeleteCellMove,
    DeleteType,
    ExportFileType,
    FilterType,
    FindType,
    InsertType,
    PasteType,
    PasteValueType,
    ReadType,
    RowInsertShift,
    SortOrder,
    WriteMode,
    WriteType,
)
from astronverse.datatable.datatable import DataTable


class TestDataTable(TestCase):
        
    def test_read_cell(self):
        dt = DataTable()
        value = dt.read_data(
            read_type=ReadType.CELL,
            row=2,
            col="B",
        )
        print(value)
        
    def test_read_row(self):
        dt = DataTable()
        values = dt.read_data(
            read_type=ReadType.ROW,
            row=2,
        )
        print(values)
        
    def test_read_column(self):
        dt = DataTable()
        values = dt.read_data(
            read_type=ReadType.COLUMN,
            col="C",
        )
        print(values)
        
    def test_read_area(self):
        dt = DataTable()
        values = dt.read_data(
            read_type=ReadType.AREA,
            start_col="A",
            start_row=1,
            end_col="C",
            end_row=3,
        )
        print(values)
    
    def test_read_all(self):
        dt = DataTable()
        values = dt.read_data(
            read_type=ReadType.AREA,
            start_col="A",
            start_row=1,
            end_col="",
            end_row=0,
        )
        print(values)
        
    def test_get_max_row(self):
        dt = DataTable()
        max_row = dt.get_max_row()
        print(max_row)
    
    def test_get_max_column(self):
        pass
    
    def test_write_cell(self):
        dt = DataTable()
        dt.write_data(
            write_type=WriteType.CELL,
            row=1,
            col="A",
            data="xxx",
            write_mode=WriteMode.INSERT,
            append_position=AppendShift.ROW,
            cell_insert_shift=CellInsertShift.RIGHT,
        )
        
    def test_write_row(self):
        dt = DataTable()
        dt.write_data(
            write_type=WriteType.ROW,
            row=1,
            start_col="B",
            data=["A1", "B1", "C1"],
            write_mode=WriteMode.INSERT,
            row_insert_shift=RowInsertShift.UP,
        )
        
    def test_write_column(self):
        dt = DataTable()
        dt.write_data(
            write_type=WriteType.COLUMN,
            row=1,
            col="C",
            start_row=2,
            data=["A11", "B11", "C11"],
            write_mode=WriteMode.INSERT,
            column_insert_shift=ColumnInsertShift.RIGHT,
        )
        
    def test_write_area(self):
        dt = DataTable()
        dt.write_data(
            write_type=WriteType.AREA,
            start_row=2,
            start_col="B",
            data=[["D5", "E5", "F5"], ["D6", "E6", "F6"]],
            write_mode=WriteMode.OVERWRITE,
        )

    def test_copy_cell(self):
        data = DataTable().copy_data(
            copy_type=CopyType.CELL,
            row=2,
            col="B",
        )
        print(data)
    
    def test_copy_row(self):
        data = DataTable().copy_data(
            copy_type=CopyType.ROW,
            row=2,
        )
        print(data)
    
    def test_copy_column(self):
        data = DataTable().copy_data(
            copy_type=CopyType.COLUMN,
            col="C",
        )
        print(data)
        
    def test_copy_area(self):
        data = DataTable().copy_data(
            copy_type=CopyType.AREA,
            start_col="A",
            start_row=1,
            end_col="C",
            end_row=3,
        )
        print(data)
        
    def test_paste_cell(self):
        DataTable().paste_data(
            paste_type=PasteType.CELL,
            row=3,
            col="D",
            paste_value_type=PasteValueType.VALUE,
        )
        
    def test_paste_row(self):
        DataTable().paste_data(
            paste_type=PasteType.ROW,
            row=4,
        )
    
    def test_paste_column(self):
        DataTable().paste_data(
            paste_type=PasteType.COLUMN,
            col="E",
        )
    
    def test_paste_area(self):
        DataTable().paste_data(
            paste_type=PasteType.AREA,
            start_row=5,
            start_col="F",
        )
    
    def test_delete_cell(self):
        DataTable().delete_data(
            delete_type=DeleteType.CELL,
            row=1,
            col="A",
            delete_cell_move=DeleteCellMove.UP,
        )
    
    def test_delete_row(self):
        DataTable().delete_data(
            delete_type=DeleteType.ROW,
            row=1,
            delete_row_move=False
        )
    
    def test_delete_column(self):
        DataTable().delete_data(
            delete_type=DeleteType.COLUMN,
            col="A",
            delete_col_move=False
        )
    
    def test_delete_area(self):
        DataTable().delete_data(
            delete_type=DeleteType.AREA,
            start_row=3,
            start_col="C",
            end_row=4,
            end_col="D",
        )
        
    def test_sort_table(self):
        DataTable().sort_table(
            col="B",
            sort_type=SortOrder.DESCENDING,
        )
        
    def test_insert_row_column(self):
        dt = DataTable()
        dt.insert_row_column(
           insert_type=InsertType.ROW,
           row=2,
           amount=1
        )
        dt.insert_row_column(
              insert_type=InsertType.COLUMN,
              col="C",
              amount=2
        )
        
    def test_insert_formula(self):
        dt = DataTable()
        dt.insert_formula(
            row=3,
            col="D",
            formula="=SUM(A3,B3)"
        )
    
    def test_set_column_title(self):
        dt = DataTable()
        dt.set_column_title(
            col="A",
            title="A New Title"
        )
    
    def test_get_column_title(self):
        dt = DataTable()
        title = dt.get_column_title(
            col="A"
        )
        print(title)
        
    def test_find_and_replace(self):
        dt = DataTable()
        data = dt.find_and_replace(
            find_type=FindType.COLUMN,
            col='B',
            find_value="third",
            replace_value="3",
            is_replace=True,
            is_case_sensitive=False,
        )
        print(data)
    
    def test_filter_data_table_column(self):
        dt = DataTable()
        filtered_dt = dt.filter_data_table(
            filter_type=FilterType.COLUMN,
            col="F",
            condition_type=ConditionType.GREATER_THAN,
            condition_value="5",
            is_case_sensitive=True,
            is_save_filtered=True,
        )
        print(filtered_dt)
        
    def test_filter_data_table_row(self):
        dt = DataTable()
        filtered_dt = dt.filter_data_table(
            filter_type=FilterType.ROW,
            row=5,
            condition_type=ConditionType.LESS_THAN,
            condition_value="8",
            is_case_sensitive=False,
            is_save_filtered=True,
        )
        print(filtered_dt)
        
    def test_filter_data_table_table(self):
        dt = DataTable()
        filtered_dt = dt.filter_data_table(
            filter_type=FilterType.TABLE,
            condition_type=ConditionType.IS_NOT_EMPTY,
            condition_value="",
            is_case_sensitive=False,
            is_save_filtered=True,
        )
        print(filtered_dt)
        
    def test_filter_data_table_date_range(self):
        dt = DataTable()
        filtered_dt = dt.filter_data_table(
            filter_type=FilterType.COLUMN,
            col="A",
            condition_type=ConditionType.DATE_BETWEEN,
            condition_value="",
            date_value="2023-01-01",
            date_range="2023-01-01,2023-12-31",
            is_case_sensitive=False,
            is_save_filtered=False,
        )
        print(filtered_dt)
        
    def test_import_data_table_from_file(self):
        dt = DataTable()
        dt.import_data_table_from_file(
            import_file_path="path/to/file.csv",
            sheet_name="Sheet1"
        )
        
    def test_export_data_table_to_file(self):
        dt = DataTable()
        dt.export_data_table_to_file(
            export_dest_path="path/to/exported_file.csv",
            export_file_name="exported_file",
            export_file_type=ExportFileType.CSV
        )
        