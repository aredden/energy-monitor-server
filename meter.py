import os
from kasa.smartstrip import SmartStrip
import kasa
import asyncio
from loggy import get_logger
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    pass
else:
    load_dotenv()

log = get_logger()

try:
    ip = os.environ["METER_IP"]
except Exception as e:
    log.exception(
        "Please make sure ENV variable METER_IP exists in the .env file at the root of project."
    )
    exit()
time_format = "%m/%d/%y-%H:%M:%S"
strip = SmartStrip(ip)
RUNNING = True


def emeter_info(plug: kasa.SmartPlug):
    w = plug.emeter_realtime
    return {
        "watts": w["power_mw"] / 1000,
        "volts": w["voltage_mv"] / 1000,
        "total_whours": w["total_wh"],
        "id": plug.alias,
    }


async def get_plug_names():
    await strip.update()
    chld = [c for c in strip.children]
    return [c.alias for c in chld]


async def update_current():
    await strip.update()


def get_plug_data(
    label
):
    return emeter_info(strip.get_plug_by_name(label.replace("_", " ")))


def kill_meter_loop():
    global RUNNING
    RUNNING = False


async def meter_loop(loop):
    while RUNNING:
        await update_current()
        await asyncio.sleep(2)
