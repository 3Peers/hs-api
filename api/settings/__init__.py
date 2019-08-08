import os
from apps.globals.utils.print_utils import print_with_color, AsciiCodes

server = 'PRODUCTION'

if os.environ.get('PY_ENV') == 'production':
    from .prod import *
elif os.environ.get('PY_ENV') == 'test':
    from .test import *
    server = 'TEST'
else:
    server = 'DEVELOPMENT'
    from .dev import *

print_with_color(f'[Info] Using {server} Settings!', AsciiCodes.BRIGHT_CYAN)