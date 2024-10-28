import os
from .cuidao import *
from .operations import *
from .mahoo import *

if os.path.exists(os.path.join(os.path.dirname(__file__), "meme_3rd_optional")):
    try:
        from .meme_3rd_optional import *
    except ModuleNotFoundError:
        pass
