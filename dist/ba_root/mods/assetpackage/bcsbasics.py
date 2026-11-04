# Released under the MIT License. See LICENSE for details.
#
# Auto-generated; do not edit by hand.
"""Asset-package wrapper for ``a-4.bcsbasics.test260831`` (bascenev1)."""

# ba_meta require api 9
# ba_meta require asset-package a-4.bcsbasics.test260831

# pylint: disable=useless-suppression
# pylint: disable=too-many-lines
# pylint: disable=too-few-public-methods, disallowed-name

from typing import TYPE_CHECKING

from bascenev1._assetref import AssetGroup

_ASSET_PACKAGE = 'a-4.bcsbasics.test260831'

if TYPE_CHECKING:
    from bascenev1._assetref import MeshHandle, TextureHandle

    class MeshGroup:
        """Asset-group type; see source for the full list."""

        ferraicar: MeshHandle
        monkeyfacelevel: MeshHandle
        monkeyfacelevelbottom: MeshHandle
        zigzagbottom: MeshHandle
        zigzagbumper: MeshHandle
        zigzagcollide: MeshHandle
        zigzaglevel: MeshHandle

    class TexturesGroup:
        """Asset-group type; see source for the full list."""

        bcsbg: TextureHandle
        blender: TextureHandle
        bnt: TextureHandle
        cartexture: TextureHandle
        cferraricarlowpolytexture: TextureHandle
        combinedtexture: TextureHandle
        moneybcs: TextureHandle
        monkeymap: TextureHandle
        welcome: TextureHandle

    #: The ``mesh`` group - 7 assets (``ferraicar``, ``monkeyfacelevel``,
    #: ``monkeyfacelevelbottom``, ``zigzagbottom``, ``zigzagbumper``, and 2
    #: more). Full list in source.
    mesh: MeshGroup

    #: The ``textures`` group - 9 assets (``bcsbg``, ``blender``, ``bnt``,
    #: ``cartexture``, ``cferraricarlowpolytexture``, and 4 more). Full list in
    #: source.
    textures: TexturesGroup

_TREE = {
    'mesh': {
        'ferraicar': 'm',
        'monkeyfacelevel': 'm',
        'monkeyfacelevelbottom': 'm',
        'zigzagbottom': 'm',
        'zigzagbumper': 'm',
        'zigzagcollide': 'm',
        'zigzaglevel': 'm',
    },
    'textures': {
        'bcsbg': 't',
        'blender': 't',
        'bnt': 't',
        'cartexture': 't',
        'cferraricarlowpolytexture': 't',
        'combinedtexture': 't',
        'moneybcs': 't',
        'monkeymap': 't',
        'welcome': 't',
    },
}


if not TYPE_CHECKING:
    mesh = AssetGroup(_ASSET_PACKAGE, _TREE['mesh'], 'mesh')
    textures = AssetGroup(_ASSET_PACKAGE, _TREE['textures'], 'textures')
