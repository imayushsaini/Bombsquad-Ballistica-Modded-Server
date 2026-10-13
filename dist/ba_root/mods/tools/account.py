# ba_meta require api 8
from __future__ import annotations

import asyncio

import _babase
import _bascenev1
import bacommon.cloud
import babase
import bascenev1 as bs
from efro.terminal import Clr
from efro.error import CommunicationError
from efro.util import strip_exception_tracebacks
from playersdata import pdata

STATUS_CHECK_INTERVAL_SECONDS = 2.0
_BROWSER_SIGN_IN_WAIT_SECONDS = 290.0


class AccountUtil:
    def __init__(self) -> None:
        print("account util init")
        _babase.app.create_async_task(
            self._run(), name='account-util-v2-proxy-sign-in'
        )

    async def _run(self) -> None:
        print("account util run")
        plus = _babase.app.plus
        if plus is None:
            print("Error: plus module not available")
            return

        if (plus.get_v1_account_state() == 'signed_in' and plus.get_v1_account_type() == 'V2') or (
            plus.accounts is not None and plus.accounts.primary is not None
        ):
            v2_name = (
                plus.accounts.primary.tag
                if (plus.accounts and plus.accounts.primary)
                else plus.get_v1_account_display_string()
            )
            print(f"{Clr.SGRN} Already logged in to V2 account: {v2_name} {Clr.RST}")
            return

        try:
            proxy = await plus.cloud.send_message_async(
                bacommon.cloud.LoginProxyRequestMessage()
            )
        except Exception as exc:
            print("error occured:", exc)
            print("Falling back to V1 account")
            if plus.accounts is not None:
                plus.accounts.set_primary_credentials(None)
            plus.sign_out_v1()
            bs.apptimer(1.0, babase.CallStrict(plus.sign_in_v1, 'Local'))
            strip_exception_tracebacks(exc)
            return

        address = plus.get_master_server_address() + proxy.url
        print("Copy this URL to your browser : " + address)

        deadline = _babase.apptime() + _BROWSER_SIGN_IN_WAIT_SECONDS
        while True:
            await asyncio.sleep(STATUS_CHECK_INTERVAL_SECONDS)
            if _babase.apptime() >= deadline:
                print("error occured ..terminating login request")
                print("Falling back to V1 account")
                if plus.accounts is not None:
                    plus.accounts.set_primary_credentials(None)
                plus.sign_out_v1()
                bs.apptimer(1.0, babase.CallStrict(plus.sign_in_v1, 'Local'))
                return

            try:
                status = await plus.cloud.send_message_async(
                    bacommon.cloud.LoginProxyStateQueryMessage(
                        proxyid=proxy.proxyid, proxykey=proxy.proxykey
                    )
                )
            except CommunicationError as exc:
                strip_exception_tracebacks(exc)
                continue
            except Exception as exc:
                print("Login proxy status check failed:", exc)
                strip_exception_tracebacks(exc)
                continue

            if status.state is status.State.FAIL:
                print("error occured ..terminating login request")
                print("Falling back to V1 account")
                if plus.accounts is not None:
                    plus.accounts.set_primary_credentials(None)
                plus.sign_out_v1()
                bs.apptimer(1.0, babase.CallStrict(plus.sign_in_v1, 'Local'))
                return

            if status.state is status.State.SUCCESS:
                break

        assert status.credentials is not None
        plus.accounts.set_primary_credentials(status.credentials)

        # Courtesy: tell the server we're done with the proxy
        try:
            await plus.cloud.send_message_async(
                bacommon.cloud.LoginProxyCompleteMessage(proxyid=proxy.proxyid)
            )
        except Exception as exc:
            strip_exception_tracebacks(exc)

        # Wait briefly for primary account credentials to take effect
        await asyncio.sleep(1.0)
        v2_name = (
            plus.accounts.primary.tag
            if (plus.accounts and plus.accounts.primary)
            else plus.get_v1_account_display_string()
        )
        print(f"{Clr.SGRN} Logged in as: {v2_name} {Clr.RST}")


def updateOwnerIps():
    if "owner" in pdata.get_roles():
        accountIds = pdata.get_roles()["owner"]["ids"]
        profiles = pdata.get_profiles()

        for account_id in accountIds:
            if account_id in profiles:
                profile = profiles[account_id]
                if "lastIP" in profile:
                    ip = profile["lastIP"]
                    _bascenev1.append_owner_ip(ip)
