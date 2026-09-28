# Released under the MIT License. See LICENSE for details.
#
# Auto-generated; do not edit by hand.
"""Asset-package wrapper for ``a-4.testasset.test260724a`` (bascenev1)."""

# ba_meta require api 9
# ba_meta require asset-package a-4.testasset.test260724a

# pylint: disable=useless-suppression
# pylint: disable=too-many-lines
# pylint: disable=too-few-public-methods, disallowed-name

__asset_package__ = 'a-4.testasset.test260724a'

from typing import TYPE_CHECKING

from bascenev1._assetwrap import AssetDir

if TYPE_CHECKING:
    import bascenev1

    class TextureGroup:
        """Asset-group type; see source for the full list."""

        bnt: bascenev1.Texture

    #: The ``texture`` group - 1 asset (``bnt``). Full list in source.
    texture: TextureGroup

_TREE = {'texture': {'bnt': 't'}}


if not TYPE_CHECKING:
    texture = AssetDir(__asset_package__, _TREE['texture'], 'texture')
