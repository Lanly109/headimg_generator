import os
from .cuidao import *
from .operations import *

if os.path.exists(os.path.join(os.path.dirname(__file__), "meme_3rd_optional")):
    from .meme_3rd_optional import *
