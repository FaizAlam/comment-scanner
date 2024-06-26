"""This module provides methods for parsing comments from Javascript code."""

from comment_scanner.parsers import common


def extract_comments(code):
    """Extracts a list of comments from the given Javascript source code.

    Comments are represented with the Comment class found in the common module.
    Javascript comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
        - Multi-line comments begin with '/*' and end with '*/' and can span
          multiple lines of code.
    If a multi-line comment does not terminatebefore EOF is reached,
    then an exception is raised.

    Args:
        code: String containing code to extract comments from.
    Returns:
        Python list of common.Comment in the order that they appear in the code.
    Raises:
        common.UnterminatedCommentError: Raised if an unterminated multi-line
        comment is encountered.
    """
    state = 0
    current_comment = ''
    comments = []
    line_counter = 1
    multiline_counter = 1
    comment_start = 1
    string_char = ''

    for char in code:
        if state == 0:
            # Waiting for comment start character or beginning of string.
            if char == '/':
                state = 1
            elif char in ('"', "'"):
                string_char = char
                state = 5

        elif state == 1:
            # Found comment start character, classify next character and
            # determine if single or multi-line comment.
            if char == '/':
                state = 2
            elif char == '*':
                comment_start = line_counter
                state = 3
            else:
                state = 0

        elif state == 2:
            # In single-line comment, read characters until EOL.
            if char == '\n':
                comment = common.Comment(current_comment, line_counter)
                comments.append(comment)
                current_comment = ''
                state = 0
            else:
                current_comment += char

        elif state == 3:
            # In multi-line comment, add characters until '*' is encountered.
            if char == '*':
                state = 4
                multiline_counter = line_counter
            else:
                current_comment += char

        elif state == 4:
            # In multi-line comment with asterisk found. Determine if comment is ending.
            if char == '/':
                line_no = [x for x in range(comment_start, multiline_counter + 1)]
                comment = common.Comment(current_comment, line_no, multiline=True)
                comments.append(comment)
                current_comment = ''
                state = 0
            else:
                current_comment += '*'
                # Care for multiple '*' in a row
                if char != '*':
                    current_comment += char
                    state = 3

        elif state == 5:
            # In string literal, expect literal end or escape character.
            if char == string_char:
                state = 0
            elif char == '\\':
                state = 6

        elif state == 6:
            # In string literal, escaping current char.
            state = 5

        if char == '\n':
            line_counter += 1

    # EOF.
    if state in (3, 4):
        raise common.UnterminatedCommentError()
    if state == 2:
        # Was in single-line comment. Create comment.
        comment = common.Comment(current_comment, line_counter)
        comments.append(comment)
    return comments
