"""This module provides constructs common to all comment parsers."""
from typing import Union, List


class Error(Exception):
    """Base Error class for all comment parsers."""


class FileError(Error):
    """Raised if there is an issue reading a given file"""


class UnterminatedCommentError(Error):
    """Raised if an unterminated multi line comment is encountered"""


class Comment():
    """Represents comments found in source files"""

    def __init__(self,
                 text: str,
                 line_number: Union[int,
                                    List],
                 multiline: bool = False):
        """Initializes comment

        Args:
            -text: String text of comment.
            -line_number: Line number (int or List) comment was found on
            -multiline: Boolean whether this comment was a multiline comment
        """

        self._text = text
        self._line_number = line_number
        self._multiline = multiline

    def text(self) -> str:
        """Returns the comment's text(string)"""
        return self._text

    def line_number(self) -> Union[int, List]:
        """Returns the line number the comment was found on(int or List)"""
        return self._line_number

    def is_multiline(self) -> bool:
        """Returns whether this comment was a multiline comment."""
        return self._multiline

    def __str__(self) -> str:
        return self._text

    def __repr__(self) -> str:
        return f'Comment({self._text}, {self._line_number}, {self._multiline})'
