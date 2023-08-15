# Released under the MIT License. See LICENSE for details.
#
"""Defines button for co-op games."""

from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any, Callable


class TournamentButton:
    """Button showing a tournament in coop window."""

    def __init__(
        self,
        parent: bui.Widget,
        x: float,
        y: float,
        select: bool,
        on_pressed: Callable[[TournamentButton], None],
    ) -> None:
        self._r = 'coopSelectWindow'
        sclx = 300
        scly = 195.0
        self.on_pressed = on_pressed
        self.lsbt = bui.getmesh('level_select_button_transparent')
        self.lsbo = bui.getmesh('level_select_button_opaque')
        self.allow_ads = False
        self.tournament_id: str | None = None
        self.time_remaining: int = 0
        self.has_time_remaining: bool = False
        self.leader: Any = None
        self.required_league: str | None = None
        self.button = btn = bui.buttonwidget(
            parent=parent,
            position=(x + 23, y + 4),
            size=(sclx, scly),
            label='',
            button_type='square',
            autoselect=True,
            on_activate_call=bui.WeakCall(self._pressed),
        )
        bui.widget(
            edit=btn,
            show_buffer_bottom=50,
            show_buffer_top=50,
            show_buffer_left=400,
            show_buffer_right=200,
        )
        if select:
            bui.containerwidget(
                edit=parent, selected_child=btn, visible_child=btn
            )
        image_width = sclx * 0.85 * 0.75

        self.image = bui.imagewidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 21 + sclx * 0.5 - image_width * 0.5, y + scly - 150),
            size=(image_width, image_width * 0.5),
            mesh_transparent=self.lsbt,
            mesh_opaque=self.lsbo,
            texture=bui.gettexture('black'),
            opacity=0.2,
            mask_texture=bui.gettexture('mapPreviewMask'),
        )

        self.lock_image = bui.imagewidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 21 + sclx * 0.5 - image_width * 0.25, y + scly - 150),
            size=(image_width * 0.5, image_width * 0.5),
            texture=bui.gettexture('lock'),
            opacity=0.0,
        )

        self.button_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 20 + sclx * 0.5, y + scly - 35),
            size=(0, 0),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=sclx * 0.76,
            scale=0.85,
            color=(0.8, 1.0, 0.8, 1.0),
        )

        header_color = (0.43, 0.4, 0.5, 1)
        value_color = (0.6, 0.6, 0.6, 1)

        x_offs = 0
        bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 360, y + scly - 20),
            size=(0, 0),
            h_align='center',
            text=bui.Lstr(resource=self._r + '.entryFeeText'),
            v_align='center',
            maxwidth=100,
            scale=0.9,
            color=header_color,
            flatness=1.0,
        )

        self.entry_fee_text_top = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 360, y + scly - 60),
            size=(0, 0),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=60,
            scale=1.3,
            color=value_color,
            flatness=1.0,
        )
        self.entry_fee_text_or = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 360, y + scly - 90),
            size=(0, 0),
            h_align='center',
            text='',
            v_align='center',
            maxwidth=60,
            scale=0.5,
            color=value_color,
            flatness=1.0,
        )
        self.entry_fee_text_remaining = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 360, y + scly - 90),
            size=(0, 0),
            h_align='center',
            text='',
            v_align='center',
            maxwidth=60,
            scale=0.5,
            color=value_color,
            flatness=1.0,
        )

        self.entry_fee_ad_image = bui.imagewidget(
            parent=parent,
            size=(40, 40),
            draw_controller=btn,
            position=(x + 360 - 20, y + scly - 140),
            opacity=0.0,
            texture=bui.gettexture('tv'),
        )

        x_offs += 50

        bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 447 + x_offs, y + scly - 20),
            size=(0, 0),
            h_align='center',
            text=bui.Lstr(resource=self._r + '.prizesText'),
            v_align='center',
            maxwidth=130,
            scale=0.9,
            color=header_color,
            flatness=1.0,
        )

        self.button_x = x
        self.button_y = y
        self.button_scale_y = scly

        xo2 = 0
        prize_value_scale = 1.5

        self.prize_range_1_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 355 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='right',
            v_align='center',
            maxwidth=50,
            text='-',
            scale=0.8,
            color=header_color,
            flatness=1.0,
        )
        self.prize_value_1_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 380 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='left',
            text='-',
            v_align='center',
            maxwidth=100,
            scale=prize_value_scale,
            color=value_color,
            flatness=1.0,
        )

        self.prize_range_2_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 355 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='right',
            v_align='center',
            maxwidth=50,
            scale=0.8,
            color=header_color,
            flatness=1.0,
        )
        self.prize_value_2_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 380 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='left',
            text='',
            v_align='center',
            maxwidth=100,
            scale=prize_value_scale,
            color=value_color,
            flatness=1.0,
        )

        self.prize_range_3_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 355 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='right',
            v_align='center',
            maxwidth=50,
            scale=0.8,
            color=header_color,
            flatness=1.0,
        )
        self.prize_value_3_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 380 + xo2 + x_offs, y + scly - 93),
            size=(0, 0),
            h_align='left',
            text='',
            v_align='center',
            maxwidth=100,
            scale=prize_value_scale,
            color=value_color,
            flatness=1.0,
        )

        bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 620 + x_offs, y + scly - 20),
            size=(0, 0),
            h_align='center',
            text=bui.Lstr(resource=self._r + '.currentBestText'),
            v_align='center',
            maxwidth=180,
            scale=0.9,
            color=header_color,
            flatness=1.0,
        )
        self.current_leader_name_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(
                x + 620 + x_offs - (170 / 1.4) * 0.5,
                y + scly - 60 - 40 * 0.5,
            ),
            selectable=True,
            click_activate=True,
            autoselect=True,
            on_activate_call=bui.WeakCall(self._show_leader),
            size=(170 / 1.4, 40),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=170,
            scale=1.4,
            color=value_color,
            flatness=1.0,
        )
        self.current_leader_score_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 620 + x_offs, y + scly - 113 + 10),
            size=(0, 0),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=170,
            scale=1.8,
            color=value_color,
            flatness=1.0,
        )

        self.more_scores_button = bui.buttonwidget(
            parent=parent,
            position=(x + 620 + x_offs - 60, y + scly - 50 - 125),
            color=(0.5, 0.5, 0.6),
            textcolor=(0.7, 0.7, 0.8),
            label='-',
            size=(120, 40),
            autoselect=True,
            up_widget=self.current_leader_name_text,
            text_scale=0.6,
            on_activate_call=bui.WeakCall(self._show_scores),
        )
        bui.widget(
            edit=self.current_leader_name_text,
            down_widget=self.more_scores_button,
        )

        bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 820 + x_offs, y + scly - 20),
            size=(0, 0),
            h_align='center',
            text=bui.Lstr(resource=self._r + '.timeRemainingText'),
            v_align='center',
            maxwidth=180,
            scale=0.9,
            color=header_color,
            flatness=1.0,
        )
        self.time_remaining_value_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 820 + x_offs, y + scly - 68),
            size=(0, 0),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=180,
            scale=2.0,
            color=value_color,
            flatness=1.0,
        )
        self.time_remaining_out_of_text = bui.textwidget(
            parent=parent,
            draw_controller=btn,
            position=(x + 820 + x_offs, y + scly - 110),
            size=(0, 0),
            h_align='center',
            text='-',
            v_align='center',
            maxwidth=120,
            scale=0.72,
            color=(0.4, 0.4, 0.5),
            flatness=1.0,
        )

    def _pressed(self) -> None:
        self.on_pressed(self)

    def _show_leader(self) -> None:
        # pylint: disable=cyclic-import
        from bauiv1lib.account.viewer import AccountViewerWindow

        tournament_id = self.tournament_id

        # FIXME: This assumes a single player entry in leader; should expand
        #  this to work with multiple.
        if (
            tournament_id is None
            or self.leader is None
            or len(self.leader[2]) != 1
        ):
            bui.getsound('error').play()
            return
        bui.getsound('swish').play()
        AccountViewerWindow(
            account_id=self.leader[2][0].get('a', None),
            profile_id=self.leader[2][0].get('p', None),
            position=self.current_leader_name_text.get_screen_space_center(),
        )

    def _show_scores(self) -> None:
        # pylint: disable=cyclic-import
        from bauiv1lib.tournamentscores import TournamentScoresWindow

        tournament_id = self.tournament_id
        if tournament_id is None:
            bui.getsound('error').play()
            return

        TournamentScoresWindow(
            tournament_id=tournament_id,
            position=self.more_scores_button.get_screen_space_center(),
        )

    def update_for_data(self, entry: dict[str, Any]) -> None:
        """Update for new incoming data."""
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches

        plus = bui.app.plus
        assert plus is not None

        assert bui.app.classic is not None
        prize_y_offs = (
            34
            if 'prizeRange3' in entry
            else 20
            if 'prizeRange2' in entry
            else 12
        )
        x_offs = 90

        # pylint: disable=useless-suppression
        # pylint: disable=unbalanced-tuple-unpacking
        (
            pr1,
            pv1,
            pr2,
            pv2,
            pr3,
            pv3,
        ) = bui.app.classic.get_tournament_prize_strings(entry)
        # pylint: enable=unbalanced-tuple-unpacking
        # pylint: enable=useless-suppression

        enabled = 'requiredLeague' not in entry
        bui.buttonwidget(
            edit=self.button,
            color=(0.5, 0.7, 0.2) if enabled else (0.5, 0.5, 0.5),
        )
        bui.imagewidget(edit=self.lock_image, opacity=0.0 if enabled else 1.0)
        bui.textwidget(
            edit=self.prize_range_1_text,
            text='-' if pr1 == '' else pr1,
            position=(
                self.button_x + 365 + x_offs,
                self.button_y + self.button_scale_y - 93 + prize_y_offs,
            ),
        )

        # We want to draw values containing tickets a bit smaller
        # (scratch that; we now draw medals a bit bigger).
        ticket_char = bui.charstr(bui.SpecialChar.TICKET_BACKING)
        prize_value_scale_large = 1.0
        prize_value_scale_small = 1.0

        bui.textwidget(
            edit=self.prize_value_1_text,
            text='-' if pv1 == '' else pv1,
            scale=prize_value_scale_large
            if ticket_char not in pv1
            else prize_value_scale_small,
            position=(
                self.button_x + 380 + x_offs,
                self.button_y + self.button_scale_y - 93 + prize_y_offs,
            ),
        )

        bui.textwidget(
            edit=self.prize_range_2_text,
            text=pr2,
            position=(
                self.button_x + 365 + x_offs,
                self.button_y + self.button_scale_y - 93 - 45 + prize_y_offs,
            ),
        )
        bui.textwidget(
            edit=self.prize_value_2_text,
            text=pv2,
            scale=prize_value_scale_large
            if ticket_char not in pv2
            else prize_value_scale_small,
            position=(
                self.button_x + 380 + x_offs,
                self.button_y + self.button_scale_y - 93 - 45 + prize_y_offs,
            ),
        )

        bui.textwidget(
            edit=self.prize_range_3_text,
            text=pr3,
            position=(
                self.button_x + 365 + x_offs,
                self.button_y + self.button_scale_y - 93 - 90 + prize_y_offs,
            ),
        )
        bui.textwidget(
            edit=self.prize_value_3_text,
            text=pv3,
            scale=prize_value_scale_large
            if ticket_char not in pv3
            else prize_value_scale_small,
            position=(
                self.button_x + 380 + x_offs,
                self.button_y + self.button_scale_y - 93 - 90 + prize_y_offs,
            ),
        )

        leader_name = '-'
        leader_score: str | bui.Lstr = '-'
        if entry['scores']:
            score = self.leader = copy.deepcopy(entry['scores'][0])
            leader_name = score[1]
            leader_score = (
                bui.timestring((score[0] * 10) / 1000.0, centi=True)
                if entry['scoreType'] == 'time'
                else str(score[0])
            )
        else:
            self.leader = None

        bui.textwidget(
            edit=self.current_leader_name_text, text=bui.Lstr(value=leader_name)
        )
        bui.textwidget(edit=self.current_leader_score_text, text=leader_score)
        bui.buttonwidget(
            edit=self.more_scores_button,
            label=bui.Lstr(resource=self._r + '.seeMoreText'),
        )
        out_of_time_text: str | bui.Lstr = (
            '-'
            if 'totalTime' not in entry
            else bui.Lstr(
                resource=self._r + '.ofTotalTimeText',
                subs=[
                    (
                        '${TOTAL}',
                        bui.timestring(entry['totalTime'], centi=False),
                    )
                ],
            )
        )
        bui.textwidget(
            edit=self.time_remaining_out_of_text, text=out_of_time_text
        )

        self.time_remaining = entry['timeRemaining']
        self.has_time_remaining = entry is not None
        self.tournament_id = entry['tournamentID']
        self.required_league = (
            None if 'requiredLeague' not in entry else entry['requiredLeague']
        )

        assert bui.app.classic is not None
        game = bui.app.classic.accounts.tournament_info[self.tournament_id][
            'game'
        ]

        if game is None:
            bui.textwidget(edit=self.button_text, text='-')
            bui.imagewidget(
                edit=self.image, texture=bui.gettexture('black'), opacity=0.2
            )
        else:
            campaignname, levelname = game.split(':')
            campaign = bui.app.classic.getcampaign(campaignname)
            max_players = bui.app.classic.accounts.tournament_info[
                self.tournament_id
            ]['maxPlayers']
            txt = bui.Lstr(
                value='${A} ${B}',
                subs=[
                    ('${A}', campaign.getlevel(levelname).displayname),
                    (
                        '${B}',
                        bui.Lstr(
                            resource='playerCountAbbreviatedText',
                            subs=[('${COUNT}', str(max_players))],
                        ),
                    ),
                ],
            )
            bui.textwidget(edit=self.button_text, text=txt)
            bui.imagewidget(
                edit=self.image,
                texture=bui.gettexture(
                    campaign.getlevel(levelname).preview_texture_name
                ),
                opacity=1.0 if enabled else 0.5,
            )

        fee = entry['fee']

        if fee is None:
            fee_var = None
        elif fee == 4:
            fee_var = 'price.tournament_entry_4'
        elif fee == 3:
            fee_var = 'price.tournament_entry_3'
        elif fee == 2:
            fee_var = 'price.tournament_entry_2'
        elif fee == 1:
            fee_var = 'price.tournament_entry_1'
        else:
            if fee != 0:
                print('Unknown fee value:', fee)
            fee_var = 'price.tournament_entry_0'

        self.allow_ads = allow_ads = entry['allowAds']

        final_fee: int | None = (
            None
            if fee_var is None
            else plus.get_v1_account_misc_read_val(fee_var, '?')
        )

        final_fee_str: str | bui.Lstr
        if fee_var is None:
            final_fee_str = ''
        else:
            if final_fee == 0:
                final_fee_str = bui.Lstr(resource='getTicketsWindow.freeText')
            else:
                final_fee_str = bui.charstr(
                    bui.SpecialChar.TICKET_BACKING
                ) + str(final_fee)

        assert bui.app.classic is not None
        ad_tries_remaining = bui.app.classic.accounts.tournament_info[
            self.tournament_id
        ]['adTriesRemaining']
        free_tries_remaining = bui.app.classic.accounts.tournament_info[
            self.tournament_id
        ]['freeTriesRemaining']

        # Now, if this fee allows ads and we support video ads, show
        # the 'or ad' version.
        if allow_ads and bui.has_video_ads():
            ads_enabled = bui.have_incentivized_ad()
            bui.imagewidget(
                edit=self.entry_fee_ad_image,
                opacity=1.0 if ads_enabled else 0.25,
            )
            or_text = (
                bui.Lstr(resource='orText', subs=[('${A}', ''), ('${B}', '')])
                .evaluate()
                .strip()
            )
            bui.textwidget(edit=self.entry_fee_text_or, text=or_text)
            bui.textwidget(
                edit=self.entry_fee_text_top,
                position=(
                    self.button_x + 360,
                    self.button_y + self.button_scale_y - 60,
                ),
                scale=1.3,
                text=final_fee_str,
            )

            # Possibly show number of ad-plays remaining.
            bui.textwidget(
                edit=self.entry_fee_text_remaining,
                position=(
                    self.button_x + 360,
                    self.button_y + self.button_scale_y - 146,
                ),
                text=''
                if ad_tries_remaining in [None, 0]
                else ('' + str(ad_tries_remaining)),
                color=(0.6, 0.6, 0.6, 1 if ads_enabled else 0.2),
            )
        else:
            bui.imagewidget(edit=self.entry_fee_ad_image, opacity=0.0)
            bui.textwidget(edit=self.entry_fee_text_or, text='')
            bui.textwidget(
                edit=self.entry_fee_text_top,
                position=(
                    self.button_x + 360,
                    self.button_y + self.button_scale_y - 80,
                ),
                scale=1.3,
                text=final_fee_str,
            )

            # Possibly show number of free-plays remaining.
            bui.textwidget(
                edit=self.entry_fee_text_remaining,
                position=(
                    self.button_x + 360,
                    self.button_y + self.button_scale_y - 100,
                ),
                text=(
                    ''
                    if (free_tries_remaining in [None, 0] or final_fee != 0)
                    else ('' + str(free_tries_remaining))
                ),
                color=(0.6, 0.6, 0.6, 1),
            )
