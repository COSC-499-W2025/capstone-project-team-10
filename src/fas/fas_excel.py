import openpyxl
from typing import Dict, Any

def extract_excel_data(file_path: str) -> Dict[str, Any]:
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=False)
        sheet_names = workbook.sheetnames

        metadata = {
            "sheet_count": len(sheet_names),
            "sheet_names": sheet_names,
        }

        # Workbook document properties
        props = workbook.properties
        metadata.update({
            "creator": props.creator,
            "last_modified_by": props.lastModifiedBy,
            "created": str(props.created) if props.created else None,
            "modified": str(props.modified) if props.modified else None,
            "title": props.title,
            "subject": props.subject,
            "keywords": props.keywords,
            "category": props.category,
            "description": props.description
        })

        # Per sheet stats
        # All the stats we can gather without reading all cell values
        sheet_stats = {}
        for sheet in workbook.worksheets:
            formulas = sum(1 for row in sheet.iter_rows() for cell in row if cell.value and str(cell.value).startswith("="))

            merged_cells = len(sheet.merged_cells.ranges)
            sheet_stats[sheet.title] = {
                "max_row": sheet.max_row,
                "max_column": sheet.max_column,
                "formulas": formulas,
                "merged_cells": merged_cells
            }
        metadata["sheet_stats"] = sheet_stats

        workbook.close()
        return metadata

    except Exception as e:
        return {"error": str(e)}
