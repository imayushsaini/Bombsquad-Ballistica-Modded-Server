# ba_meta require api 8
from __future__ import annotations

import babase
import bauiv1 as bui
import bascenev1 as bs
import logging
from efro.error import CommunicationError
from playersData import pdata
import bacommon.cloud

STATUS_CHECK_INTERVAL_SECONDS = 2.0


class AccountUtil:
    def __init__(self):
        self._proxyid: str | None = None
        self._proxykey: str | None = None
        bs.sign_out_v1()
        babase.app.cloud.send_message_cb(bacommon.cloud.LoginProxyRequestMessage(),
                                     on_response=babase.Call(self._on_proxy_request_response))

    def _on_proxy_request_response(self, response: bacommon.cloud.LoginProxyRequestResponse | Exception) -> None:
        if isinstance(response, Exception):
            logging.error("error occured")
            logging.critical("Falling back to V1 account")
            bs.sign_in_v1('Local')
            return
        address = bs.get_master_server_address(
            version=2) + response.url
        logging.debug("Copy this URL to your browser : " + address)
        self._proxyid = response.proxyid
        self._proxykey = response.proxykey
        bs.timer(STATUS_CHECK_INTERVAL_SECONDS,
                 babase.Call(self._ask_for_status))

    def _ask_for_status(self) -> None:
        assert self._proxyid is not None
        assert self._proxykey is not None
        babase.app.cloud.send_message_cb(
            bacommon.cloud.LoginProxyStateQueryMessage(
                proxyid=self._proxyid, proxykey=self._proxykey),
            on_response=babase.Call(self._got_status))

    def _got_status(
        self, response: bacommon.cloud.LoginProxyStateQueryResponse | Exception
    ) -> None:
        # For now, if anything goes wrong on the server-side, just abort
        # with a vague error message. Can be more verbose later if need be.
        if (isinstance(response, bacommon.cloud.LoginProxyStateQueryResponse)
                and response.state is response.State.FAIL):
            logging.error("error occured ..terminating login request")
            logging.critical("Falling back to V1 account")
            bs.sign_in_v1('Local')

        # If we got a token, set ourself as signed in. Hooray!
        if (isinstance(response, bacommon.cloud.LoginProxyStateQueryResponse)
                and response.state is response.State.SUCCESS):
            assert response.credentials is not None
            babase.app.accounts_v2.set_primary_credentials(response.credentials)

            bs.timer(3, self._logged_in)

            return

        # If we're still waiting, ask again soon.
        if (isinstance(response, Exception)
                or response.state is response.State.WAITING):
            bs.timer(STATUS_CHECK_INTERVAL_SECONDS,
                     babase.Call(self._ask_for_status))

    def _logged_in(self):
        logging.info("Logged in as: " +
                     bs.get_v1_account_display_string())


def updateOwnerIps():
    if "owner" in pdata.get_roles():
        accountIds = pdata.get_roles()["owner"]["ids"]
        profiles = pdata.get_profiles()

        for account_id in accountIds:
            if account_id in profiles:
                profile = profiles[account_id]
                if "lastIP" in profile:
                    ip = profile["lastIP"]
                    _babase.append_owner_ip(ip)
