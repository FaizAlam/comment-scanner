from comment_scanner.parsers import python_parser
from comment_scanner.parsers import js_parser
from comment_scanner.parsers import c_parser
from comment_scanner.parsers import common
import sys
from typing import List, Optional
import argparse
import tempfile
import os

has_magic = True
try:
    from magic import magic
except ImportError:
    has_magic = False


MIME_MAP = {
    'text/x-c': c_parser,  # C
    'text/x-c++': c_parser,  # C++
    'text/x-c#': c_parser,  # Csharp
    'text/x-java': c_parser,  # Java
    'text/x-javascript': js_parser,  # javascript
    'text/x-python': python_parser,  # python/python3
    'text/x-go': c_parser,  # GoLang
}


class Error(Exception):
    """Base Error class in this module."""


class UnsupportedError(Error):
    """Raised when trying to extract comments from an unsupported MIME type."""


class ParseError(Error):
    """Raised when a parser issue is encountered."""


def fetch_from_file(filename: str, mime: Optional[str] = None) -> List[common.Comment]:
    """Extracts and returns the comments from the given file.

    Args:
      filename: String name of the file to extract comments from.
      mime: Optional MIME type for file (str). Note some MIME types accepted
        don't comply with RFC2045. If not given, an attempt to deduce the
        MIME type will occur.
    Returns:
      Python list of parsers.common.Comment in the order that they appear in the file.
    Raises:
      UnsupportedError: If filename is of an unsupported MIME type.
    """
    if not mime:
        if not has_magic:
            raise ImportError('python-magic was not imported')
        mime = magic.from_file(filename, mime=True)
        if isinstance(mime, bytes):
            mime = mime.decode('utf-8')

    if mime not in MIME_MAP:
        raise UnsupportedError(f"Unsupported MIME type {mime}")

    with open(filename, 'r', encoding='utf-8') as code:
        try:
            parser = MIME_MAP[mime]
            return parser.extract_comments(code.read())
        except common.Error as e:
            raise ParseError() from e


def fetch_from_str(code: str, mime: Optional[str] = None
                   ) -> List[common.Comment]:
    """Extracts and returns comments from the given string

    Args:
      code: String      containing code to extract comments from
      mime: Optional MIME type for code (str).
    Returns:
      Python list of parsers.common.Comment in the order that they appear in the code
    Raises:
      UnsupportedError: If code is of an unsupported MIME type.
    """

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(code.encode('utf-8'))
        tmp_file_path = tmp_file.name

    comments = fetch_from_file(tmp_file_path, mime)

    try:
        os.remove(tmp_file_path)
    except Exception as e:
        print("Error removing temporary file:", e)

    return comments


def main():
    """Extracts comments from files and prints them to stdout"""
    parser = argparse.ArgumentParser(
        description="Extracts comments from files and prints them to stdout"
    )
    parser.add_argument('filename', nargs='+', help='File to extract comments from')
    args = parser.parse_args()

    for filename in args.filename:
        try:
            comments = fetch_from_file(filename)
            return comments
        except Error as exc:
            sys.stderr.write(str(exc))


if __name__ == "__main__":
    main()
