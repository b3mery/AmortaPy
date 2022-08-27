from __future__ import annotations

"""Helper utility functions
"""

def build_inline_css_style_sheet(css_file_path:str|bytes, encoding:str='utf-8') -> str|None:
    """Read a .CSS file and wrap it in inline CSS `<style> </style>`

    Args:
        css_file_path (str | bytes): Path to CSS File
        encoding (str, optional): Files Encoding. Defaults to 'utf-8'.

    Returns:
        str|None: Inline CSS String | if error None
    """
    try:
        with open(css_file_path,encoding=encoding, mode='r') as file:
            return f"<style> {file.read()} </style>"
    except FileNotFoundError:
        return None