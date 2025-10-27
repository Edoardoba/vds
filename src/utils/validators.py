import csv
from io import StringIO
from fastapi import UploadFile
import magic
from typing import Optional

from config import settings


async def validate_csv_file(file: UploadFile) -> bool:
    """
    Validate uploaded CSV file
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        True if file is valid CSV
        
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
    
    # Check content type
    if file.content_type and not file.content_type.startswith(('text/csv', 'application/csv', 'text/plain')):
        raise ValueError(f"Invalid content type: {file.content_type}. Expected CSV file")
    
    # Read and validate CSV content
    try:
        # Reset file pointer
        await file.seek(0)
        
        # Read first chunk to validate CSV format
        chunk = await file.read(8192)  # Read first 8KB
        
        if not chunk:
            raise ValueError("File is empty")
        
        # Try to decode as text
        try:
            text_content = chunk.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = chunk.decode('latin-1')
            except UnicodeDecodeError:
                raise ValueError("File encoding not supported. Please use UTF-8 or Latin-1")
        
        # Validate CSV format by trying to parse it
        csv_reader = csv.Sniffer()
        sample = text_content[:1024]  # Use first 1KB for sniffing
        
        try:
            dialect = csv_reader.sniff(sample, delimiters=',;\t')
            if not csv_reader.has_header(sample):
                # Optional: You might want to require headers
                pass
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        
        # Additional validation: check if we can read at least one row
        string_buffer = StringIO(text_content)
        reader = csv.reader(string_buffer, dialect)
        
        try:
            rows_read = 0
            for row in reader:
                rows_read += 1
                if rows_read >= 2:  # Check header + at least one data row
                    break
            
            if rows_read == 0:
                raise ValueError("CSV file appears to be empty")
                
        except csv.Error as e:
            raise ValueError(f"Error reading CSV content: {str(e)}")
        
        # Reset file pointer for actual upload
        await file.seek(0)
        
        return True
        
    except Exception as e:
        # Reset file pointer even if validation fails
        await file.seek(0)
        if isinstance(e, ValueError):
            raise e
        else:
            raise ValueError(f"File validation error: {str(e)}")


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
    Detect MIME type of file content using python-magic
    
    Args:
        file_content: Binary content of the file
        
    Returns:
        MIME type string or None if detection fails
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_buffer(file_content)
    except Exception:
        return None
