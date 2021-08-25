# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Pylint checker to verify header compliance"""

from pylint.checkers import BaseChecker
from pylint.interfaces import IRawChecker

class LCAHeaderChecker(BaseChecker):
    """Check that files will always start with the required Equinor ASA
    header"""

    __implements__ = IRawChecker

    name = 'equinor-header'
    priority = -1
    msgs = {
        'W5001': (
            'Missing copyright header',
            'missing-equinor-header',
            'All source files should contain Equinor copyright header.'
        ),
    }
    options = ()

    def process_module(self, node):
        """process a module
        the module's content is accessible via node.stream() function
        """

        legal_copyright = ('Copyright (c) Equinor ASA. '
                           'All rights reserved.')

        with node.stream() as stream:
            for line in stream:
                if isinstance(line, bytes):
                    # Assume UTF-8 for simplicity
                    line = line.decode('utf-8')
                if line.lstrip().startswith('#'):
                    if legal_copyright in line:
                        return
                elif not line.lstrip():
                    continue
                else:
                    self.add_message('missing-equinor-header', line=0)
                    return

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(LCAHeaderChecker(linter))
