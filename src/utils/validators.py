import csv
from io import StringIO, BytesIO
from fastapi import UploadFile
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Optional import for file type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    # print("⚠️  python-magic not available - using basic file type detection")

from config import settings


def clean_nan_values(data):
    """Clean NaN values from data to make it JSON serializable"""
    if isinstance(data, dict):
        return {k: clean_nan_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif pd.isna(data) or (isinstance(data, float) and np.isnan(data)):
        return None
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data) if not np.isnan(data) else None
    else:
        return data


async def validate_data_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate uploaded data file (CSV, XLSX, XLS)
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Dict with validation results and file info
        
    Raises:
        ValueError: If file validation fails
    """
    # Check file extension
    if not file.filename:
        raise ValueError("File must have a filename")
    
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ""
    if f".{file_extension}" not in settings.ALLOWED_FILE_EXTENSIONS:
        raise ValueError(f"File extension '.{file_extension}' not allowed. Allowed extensions: {settings.ALLOWED_FILE_EXTENSIONS}")
    
    # Check file size
    if hasattr(file, 'size') and file.size:
        if file.size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File size ({file.size} bytes) exceeds maximum allowed size ({settings.MAX_FILE_SIZE} bytes)")
    
    # Determine file type from extension
    file_type = 'unknown'
    if file_extension == 'csv':
        file_type = 'csv'
    elif file_extension in ['xlsx', 'xls']:
        file_type = 'excel'
    
    # Check content type (be permissive as browsers send various MIME types)
    if file.content_type:
        allowed_types = [
            # CSV types
            'text/csv', 'application/csv', 'text/plain',
            'text/comma-separated-values', 'text/x-csv', 'application/x-csv',
            # Excel types
            'application/vnd.ms-excel', 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            # Generic types
            'application/octet-stream'
        ]
        
        # Check if content type starts with any allowed type
        is_allowed = any(file.content_type.startswith(mime_type) for mime_type in allowed_types)
        
        if not is_allowed:
            # Issue warning but don't fail - rely on file extension and content validation
            print(f"⚠️  Unknown content type: {file.content_type} - proceeding with content validation")
    
    # Read and validate file content based on type
    try:
        # Reset file pointer
        await file.seek(0)
        
        if file_type == 'csv':
            # CSV validation
            validation_result = await _validate_csv_content(file)
        elif file_type == 'excel':
            # Excel validation  
            validation_result = await _validate_excel_content(file)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Reset file pointer for actual upload
        await file.seek(0)
        
        # Return comprehensive validation result
        return {
            'valid': True,
            'file_type': file_type,
            'file_extension': file_extension,
            'rows': validation_result.get('rows', 0),
            'columns': validation_result.get('columns', 0),
            'has_headers': validation_result.get('has_headers', False),
            'encoding': validation_result.get('encoding', 'unknown'),
            'preview': validation_result.get('preview', [])
        }
        
    except Exception as e:
        # Reset file pointer even if validation fails
        await file.seek(0)
        if isinstance(e, ValueError):
            raise e
        else:
            raise ValueError(f"File validation error: {str(e)}")


async def _validate_csv_content(file: UploadFile) -> Dict[str, Any]:
    """Validate CSV file content and return metadata"""
    # Read file content
    content = await file.read()
    
    if not content:
        raise ValueError("File is empty")
    
    # Try different encodings
    text_content = None
    encoding = 'unknown'
    
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            text_content = content.decode(enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    
    if text_content is None:
        raise ValueError("File encoding not supported. Please use UTF-8, Latin-1, or Windows-1252")
    
    # Use pandas for robust CSV parsing
    try:
        # Create StringIO from text content
        string_buffer = StringIO(text_content)
        
        # Try to read with pandas (more robust than csv module)
        df = pd.read_csv(string_buffer, nrows=100)  # Read first 100 rows for validation
        
        if df.empty:
            raise ValueError("CSV file appears to be empty or has no valid data")
        
        # Get preview data (first 5 rows) and clean NaN values
        preview = []
        if len(df) > 0:
            preview_raw = df.head(5).to_dict('records')
            preview = clean_nan_values(preview_raw)
        
        # Clean column names (handle NaN in column names)
        column_names = [str(col) if pd.notna(col) else f"Column_{i}" for i, col in enumerate(df.columns)]
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'has_headers': True,  # pandas assumes headers by default
            'encoding': encoding,
            'preview': preview,
            'column_names': column_names
        }
        
    except Exception as e:
        # Fallback to basic CSV validation
        return await _validate_csv_basic(text_content, encoding)


async def _validate_csv_basic(text_content: str, encoding: str) -> Dict[str, Any]:
    """Basic CSV validation fallback"""
    try:
        # Use csv.Sniffer for dialect detection
        sample = text_content[:8192]  # Use first 8KB for sniffing
        sniffer = csv.Sniffer()
        
        # Try to detect delimiter
        delimiter = ','
        try:
            dialect = sniffer.sniff(sample, delimiters=',;\t|')
            delimiter = dialect.delimiter
        except csv.Error:
            # Use default comma if sniffing fails
            pass
        
        # Parse CSV content
        string_buffer = StringIO(text_content)
        reader = csv.reader(string_buffer, delimiter=delimiter)
        
        rows = list(reader)
        
        if not rows:
            raise ValueError("CSV file appears to be empty")
        
        # Check for headers
        has_headers = len(rows) > 1 and len(rows[0]) > 0
        
        # Get preview (first 5 rows)
        preview_rows = rows[:5]
        preview = []
        
        if has_headers and len(rows) > 1:
            headers = rows[0]
            for row in preview_rows[1:]:
                if len(row) <= len(headers):
                    preview.append(dict(zip(headers, row + [''] * (len(headers) - len(row)))))
        
        return {
            'rows': len(rows) - (1 if has_headers else 0),
            'columns': len(rows[0]) if rows else 0,
            'has_headers': has_headers,
            'encoding': encoding,
            'preview': preview,
            'column_names': rows[0] if has_headers else []
        }
        
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")


async def _validate_excel_content(file: UploadFile) -> Dict[str, Any]:
    """Validate Excel file content and return metadata"""
    # Read file content
    content = await file.read()
    
    if not content:
        raise ValueError("File is empty")
    
    try:
        # Create BytesIO from content
        bytes_buffer = BytesIO(content)
        
        # Try to read Excel file with pandas
        # First, try to read just the first sheet with a limited number of rows
        df = pd.read_excel(bytes_buffer, nrows=100, sheet_name=0)
        
        if df.empty:
            raise ValueError("Excel file appears to be empty or has no valid data")
        
        # Get preview data (first 5 rows) and clean NaN values
        preview = []
        if len(df) > 0:
            preview_raw = df.head(5).to_dict('records')
            preview = clean_nan_values(preview_raw)
        
        # Clean column names (handle NaN in column names)
        column_names = [str(col) if pd.notna(col) else f"Column_{i}" for i, col in enumerate(df.columns)]
        
        # Try to get all sheet names
        bytes_buffer.seek(0)
        try:
            if file.filename.lower().endswith('.xlsx'):
                excel_file = pd.ExcelFile(bytes_buffer, engine='openpyxl')
            else:
                excel_file = pd.ExcelFile(bytes_buffer, engine='xlrd')
            sheet_names = excel_file.sheet_names
        except:
            sheet_names = ['Sheet1']  # fallback
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'has_headers': True,  # pandas assumes headers by default
            'encoding': 'binary',
            'preview': preview,
            'column_names': column_names,
            'sheet_names': sheet_names,
            'active_sheet': sheet_names[0] if sheet_names else 'Sheet1'
        }
        
    except Exception as e:
        raise ValueError(f"Invalid Excel file: {str(e)}")


# Legacy function for backward compatibility
async def validate_csv_file(file: UploadFile) -> bool:
    """Legacy function - use validate_data_file instead"""
    try:
        result = await validate_data_file(file)
        return result['valid']
    except Exception:
        return False


def validate_filename(filename: str) -> bool:
    """
    Validate filename for security and format requirements
    
    Args:
        filename: Name of the file
        
    Returns:
        True if filename is valid
        
    Raises:
        ValueError: If filename is invalid
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # Check for dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        if char in filename:
            raise ValueError(f"Filename contains invalid character: {char}")
    
    # Check filename length
    if len(filename) > 255:
        raise ValueError("Filename is too long (maximum 255 characters)")
    
    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    base_name = filename.split('.')[0].upper()
    if base_name in reserved_names:
        raise ValueError(f"Filename uses reserved name: {base_name}")
    
    return True


def get_file_mime_type(file_content: bytes) -> Optional[str]:
    """
    Detect MIME type of file content
    
    Args:
        file_content: Binary content of the file
        
    Returns:
        MIME type string or None if detection fails
    """
    if MAGIC_AVAILABLE:
        try:
            mime = magic.Magic(mime=True)
            return mime.from_buffer(file_content)
        except Exception:
            pass
    
    # Fallback: Basic file type detection for CSV
    try:
        # Try to decode as text to check if it's a CSV-like file
        text_content = file_content.decode('utf-8')
        
        # Simple heuristic: if it contains commas and newlines, likely CSV
        if ',' in text_content and '\n' in text_content:
            return 'text/csv'
        elif '\t' in text_content and '\n' in text_content:
            return 'text/tab-separated-values'
        else:
            return 'text/plain'
            
    except UnicodeDecodeError:
        try:
            # Try latin-1 encoding
            text_content = file_content.decode('latin-1')
            if ',' in text_content and '\n' in text_content:
                return 'text/csv'
            return 'text/plain'
        except Exception:
            return None
    
    except Exception:
        return None
