# Released under the MIT License. See LICENSE for details.
#
"""Defines a controller for wrangling playlist edit UIs."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import bascenev1 as bs
import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any


class PlaylistEditController:
    """Coordinates various UIs involved in playlist editing."""

    def __init__(
        self,
        sessiontype: type[bs.Session],
        existing_playlist_name: str | None = None,
        transition: str = 'in_right',
        playlist: list[dict[str, Any]] | None = None,
        playlist_name: str | None = None,
    ):
        from bascenev1 import filter_playlist
        from bauiv1lib.playlist import PlaylistTypeVars
        from bauiv1lib.playlist.edit import PlaylistEditWindow

        appconfig = bui.app.config

        # Since we may be showing our map list momentarily,
        # lets go ahead and preload all map preview textures.
        if bui.app.classic is not None:
            bui.app.classic.preload_map_preview_media()

        self._sessiontype = sessiontype

        self._editing_game = False
        self._editing_game_type: type[bs.GameActivity] | None = None
        self._pvars = PlaylistTypeVars(sessiontype)
        self._existing_playlist_name = existing_playlist_name
        self._config_name_full = self._pvars.config_name + ' Playlists'

        # Make sure config exists.
        if self._config_name_full not in appconfig:
            appconfig[self._config_name_full] = {}

        self._selected_index = 0
        if existing_playlist_name:
            self._name = existing_playlist_name

            # Filter out invalid games.
            self._playlist = filter_playlist(
                appconfig[self._pvars.config_name + ' Playlists'][
                    existing_playlist_name
                ],
                sessiontype=sessiontype,
                remove_unowned=False,
                name=existing_playlist_name,
            )
            self._edit_ui_selection = None
        else:
            if playlist is not None:
                self._playlist = playlist
            else:
                self._playlist = []
            if playlist_name is not None:
                self._name = playlist_name
            else:
                # Find a good unused name.
                i = 1
                while True:
                    self._name = (
                        self._pvars.default_new_list_name.evaluate()
                        + ((' ' + str(i)) if i > 1 else '')
                    )
                    if (
                        self._name
                        not in appconfig[self._pvars.config_name + ' Playlists']
                    ):
                        break
                    i += 1

            # Also we want it to start with 'add' highlighted since its empty
            # and that's all they can do.
            self._edit_ui_selection = 'add_button'

        assert bui.app.classic is not None
        bui.app.ui_v1.set_main_menu_window(
            PlaylistEditWindow(
                editcontroller=self, transition=transition
            ).get_root_widget()
        )

    def get_config_name(self) -> str:
        """(internal)"""
        return self._pvars.config_name

    def get_existing_playlist_name(self) -> str | None:
        """(internal)"""
        return self._existing_playlist_name

    def get_edit_ui_selection(self) -> str | None:
        """(internal)"""
        return self._edit_ui_selection

    def set_edit_ui_selection(self, selection: str) -> None:
        """(internal)"""
        self._edit_ui_selection = selection

    def getname(self) -> str:
        """(internal)"""
        return self._name

    def setname(self, name: str) -> None:
        """(internal)"""
        self._name = name

    def get_playlist(self) -> list[dict[str, Any]]:
        """Return the current state of the edited playlist."""
        return copy.deepcopy(self._playlist)

    def set_playlist(self, playlist: list[dict[str, Any]]) -> None:
        """Set the playlist contents."""
        self._playlist = copy.deepcopy(playlist)

    def get_session_type(self) -> type[bs.Session]:
        """Return the bascenev1.Session type for this edit-session."""
        return self._sessiontype

    def get_selected_index(self) -> int:
        """Return the index of the selected playlist."""
        return self._selected_index

    def get_default_list_name(self) -> bui.Lstr:
        """(internal)"""
        return self._pvars.default_list_name

    def set_selected_index(self, index: int) -> None:
        """Sets the selected playlist index."""
        self._selected_index = index

    def add_game_pressed(self) -> None:
        """(internal)"""
        from bauiv1lib.playlist.addgame import PlaylistAddGameWindow

        assert bui.app.classic is not None
        bui.app.ui_v1.clear_main_menu_window(transition='out_left')
        bui.app.ui_v1.set_main_menu_window(
            PlaylistAddGameWindow(editcontroller=self).get_root_widget()
        )

    def edit_game_pressed(self) -> None:
        """Should be called by supplemental UIs when a game is to be edited."""

        if not self._playlist:
            return
        self._show_edit_ui(
            gametype=bui.getclass(
                self._playlist[self._selected_index]['type'],
                subclassof=bs.GameActivity,
            ),
            settings=self._playlist[self._selected_index],
        )

    def add_game_cancelled(self) -> None:
        """(internal)"""
        from bauiv1lib.playlist.edit import PlaylistEditWindow

        assert bui.app.classic is not None
        bui.app.ui_v1.clear_main_menu_window(transition='out_right')
        bui.app.ui_v1.set_main_menu_window(
            PlaylistEditWindow(
                editcontroller=self, transition='in_left'
            ).get_root_widget()
        )

    def _show_edit_ui(
        self, gametype: type[bs.GameActivity], settings: dict[str, Any] | None
    ) -> None:
        self._editing_game = settings is not None
        self._editing_game_type = gametype
        assert self._sessiontype is not None
        gametype.create_settings_ui(
            self._sessiontype, copy.deepcopy(settings), self._edit_game_done
        )

    def add_game_type_selected(self, gametype: type[bs.GameActivity]) -> None:
        """(internal)"""
        self._show_edit_ui(gametype=gametype, settings=None)

    def _edit_game_done(self, config: dict[str, Any] | None) -> None:
        from bauiv1lib.playlist.edit import PlaylistEditWindow
        from bauiv1lib.playlist.addgame import PlaylistAddGameWindow

        assert bui.app.classic is not None
        if config is None:
            # If we were editing, go back to our list.
            if self._editing_game:
                bui.getsound('powerdown01').play()
                bui.app.ui_v1.clear_main_menu_window(transition='out_right')
                bui.app.ui_v1.set_main_menu_window(
                    PlaylistEditWindow(
                        editcontroller=self, transition='in_left'
                    ).get_root_widget()
                )

            # Otherwise we were adding; go back to the add type choice list.
            else:
                bui.app.ui_v1.clear_main_menu_window(transition='out_right')
                bui.app.ui_v1.set_main_menu_window(
                    PlaylistAddGameWindow(
                        editcontroller=self, transition='in_left'
                    ).get_root_widget()
                )
        else:
            # Make sure type is in there.
            assert self._editing_game_type is not None
            config['type'] = bui.get_type_name(self._editing_game_type)

            if self._editing_game:
                self._playlist[self._selected_index] = copy.deepcopy(config)
            else:
                # Add a new entry to the playlist.
                insert_index = min(
                    len(self._playlist), self._selected_index + 1
                )
                self._playlist.insert(insert_index, copy.deepcopy(config))
                self._selected_index = insert_index

            bui.getsound('gunCocking').play()
            bui.app.ui_v1.clear_main_menu_window(transition='out_right')
            bui.app.ui_v1.set_main_menu_window(
                PlaylistEditWindow(
                    editcontroller=self, transition='in_left'
                ).get_root_widget()
            )
