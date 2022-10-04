# ba_meta require api 7
from __future__ import annotations

import ba
import bacommon.cloud
import logging
from efro.error import CommunicationError



STATUS_CHECK_INTERVAL_SECONDS = 2.0

class AccountUtil:
    def __init__(self):
        self._proxyid: str | None = None
        self._proxykey: str | None = None
        ba.internal.sign_out_v1()
        ba.app.cloud.send_message_cb(bacommon.cloud.LoginProxyRequestMessage(),
                on_response=ba.Call(self._on_proxy_request_response))

    def _on_proxy_request_response(self, response: bacommon.cloud.LoginProxyRequestResponse | Exception) -> None:
        if isinstance(response, Exception):
            logging.error("error occured")
            logging.critical("Falling back to V1 account")
            ba.internal.sign_in_v1('Local')
            return
        address = ba.internal.get_master_server_address(
            version=2) + response.url
        logging.debug("Copy this URL to your browser : " +address)
        self._proxyid = response.proxyid
        self._proxykey = response.proxykey
        ba.timer(STATUS_CHECK_INTERVAL_SECONDS,
                 ba.Call(self._ask_for_status))

    def _ask_for_status(self) -> None:
        assert self._proxyid is not None
        assert self._proxykey is not None
        ba.app.cloud.send_message_cb(
            bacommon.cloud.LoginProxyStateQueryMessage(
                proxyid=self._proxyid, proxykey=self._proxykey),
            on_response=ba.Call(self._got_status))

    def _got_status(
        self, response: bacommon.cloud.LoginProxyStateQueryResponse | Exception
    ) -> None:
        # For now, if anything goes wrong on the server-side, just abort
        # with a vague error message. Can be more verbose later if need be.
        if (isinstance(response, bacommon.cloud.LoginProxyStateQueryResponse)
                and response.state is response.State.FAIL):
                logging.error("error occured ..terminating login request")
                logging.critical("Falling back to V1 account")
                ba.internal.sign_in_v1('Local')

        # If we got a token, set ourself as signed in. Hooray!
        if (isinstance(response, bacommon.cloud.LoginProxyStateQueryResponse)
                and response.state is response.State.SUCCESS):
            assert response.credentials is not None
            ba.app.accounts_v2.set_primary_credentials(response.credentials)

            ba.timer(3,self._logged_in)

            return

        # If we're still waiting, ask again soon.
        if (isinstance(response, Exception)
                or response.state is response.State.WAITING):
            ba.timer(STATUS_CHECK_INTERVAL_SECONDS,
                     ba.Call(self._ask_for_status))
    def _logged_in(self):
         logging.info("Logged in as: "+ba.internal.get_v1_account_display_string())

# ba_meta export plugin
# class AccountV2(ba.Plugin):
#     def __init__(self):
#         if(ba.internal.get_v1_account_state()=='signed_in' and ba.internal.get_v1_account_type()=='V2'):
#                 logging.debug("Account V2 is active")
#         else:
#             logging.warning("Account V2 login require ....stay tuned.")
#             ba.timer(3, ba.Call(logging.debug,"Starting Account V2 login process...."))
#             ba.timer(6,AccountUtil)
