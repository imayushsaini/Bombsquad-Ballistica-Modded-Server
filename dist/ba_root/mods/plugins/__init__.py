"""Common bits of functionality shared between all efro projects.

Things in here should be hardened, highly type-safe, and well-covered by unit
tests since they are widely used in live client and server code.

license : MIT, see LICENSE for more details.
"""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba

if TYPE_CHECKING:
    pass

# ba_meta export plugin
class Init(ba.Plugin):  # pylint: disable=too-few-public-methods
    """Initializes all of the plugins in the directory."""
