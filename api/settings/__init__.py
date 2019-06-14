import os
from globals.utils.print_utils import print_with_color, AsciiCodes

server = 'PRODUCTION'

if os.environ.get('PY_ENV') == 'production':
    from .prod import *
else:
    server = 'DEVELOPMENT'
    from .dev import *

print_with_color(f'[Info] Using {server} Settings!', AsciiCodes.BRIGHT_CYAN)