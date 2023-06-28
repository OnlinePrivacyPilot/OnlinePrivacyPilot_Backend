"""
EXCLUDE
Copyright (C) 2020-2023 megadose (Palenath)

https://github.com/megadose/holehe
https://github.com/megadose/ignorant

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
EXCLUDE
"""

import httpx
import trio
from opp import osint_imports
from holehe.localuseragent import ua
from ignorant.localuseragent import ua

async def launch_holehe(module, email, client, out):
    """
    This async function simply launches the given Holehe module with given arguments.

    """
    try:
        await module(email, client, out)
    except Exception:
        pass

async def launch_ignorant(module, phone, client, out):
    """
    This async function launches the given Ignorant module with given arguments.

    It formats if necessary the phone number accordingly to Ignorant modules requirements. 

    """
    # Workaround to split phone numbers
    # If case 1, breaks the detection of Snapchat
    tmp_split = phone.replace("+", "").split(" ")
    if len(tmp_split) == 1:
        prefix = ""
        number = tmp_split[0]
    elif len(tmp_split) >= 2:
        if len(tmp_split[0]) <= 3: # real prefix
            prefix = tmp_split[0]
            number = "".join(tmp_split[1:])
        else:
            prefix = ""
            number = "".join(tmp_split[:])
    try:
        await module(number, prefix, client, out)
    except Exception:
        pass

async def megadose_toolkit(launch_method, websites: list, target: str) -> list:
    """ This function instanciates a http client, calls given website functions and returns results in footprint format.

    Args:
        launch_method: Function to select Holehe or Ignorant launcher.
        websites (list): Website functions to call.
        target (str): Target email or phone number to investigate.

    Returns:
        list: Obtained footprints
    """
    # Def the async client
    client = httpx.AsyncClient(timeout=10)
    # Launching the modules
    out = []
    async with trio.open_nursery() as nursery:
        for website in websites:
            nursery.start_soon(launch_method, website, target, client, out)
    # Close the client
    await client.aclose()
    # Return the result
    return [
        {
            "value" : asset["domain"],
            "type" : "has_account",
            "method" : "osint_megadose",
            "positive" : True
        }
        for asset in out if asset["exists"] == True ]

def email(target_email: str) -> list:
    """ This function launches in parallel all Holehe modules with given email using `trio` library and `megadose_toolkit()`.

    Args:
        target_email (str): Email to investigate.

    Returns:
        list: Obtained footprints
    """
    return trio.run(megadose_toolkit, launch_holehe, osint_imports.WEBSITES_holehe, target_email)

def phone(target_phone: str) -> list:
    """ This function launches in parallel all Ignorant modules with given phone number using `trio` library and `megadose_toolkit()`.

    Args:
        target_phone (str): Phone number to investigate.

    Returns:
        list: Obtained footprints
    """
    return trio.run(megadose_toolkit, launch_ignorant, osint_imports.WEBSITES_ignorant, target_phone)
