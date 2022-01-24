from typing import Callable, List
import asyncio
from fastapi import FastAPI
from prometheus_client import Info, Gauge
import pydash as _
from meter import (
    get_plug_names,
    get_plug_data,
    meter_loop,
)
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from loggy import get_logger
log = get_logger()

async def shutdown_event() -> None:
    log.info("Shutting down Server", evt="shutdown")
    from meter import kill_meter_loop
    kill_meter_loop()

async def startup() -> None:
    log.info("Startup")
    labels = await get_plug_names()
    loop = asyncio.get_event_loop()
    loop.create_task(meter_loop(loop))
    plugnames = [l.replace(" ", "_") for l in labels]
    instra.add(wattage_instant(plugnames))
    log.info("Startup Complete")


app = FastAPI(on_startup=[startup], on_shutdown=[shutdown_event])

instra = (
    PrometheusFastApiInstrumentator().instrument(app).expose(app, endpoint="/query")
)

def wattage_instant(
    plug_names:List[str], device_type="HS300", 
) -> Callable[[Info], None]:
    METRIC = Gauge(
        "energy_meter",
        f"Wattage info for python-kasa.",
        labelnames=("plug_name", "metric_type", "device_type"),
    )

    def instrumentation(_info: Info) -> None:
        for plug in plug_names:
            plug = plug.replace("_", " ")
            plugdata = get_plug_data(plug)
            del plugdata['id']
            for key, val in plugdata.items():
                METRIC.labels(
                    plug_name=plug, metric_type=key, device_type=device_type
                ).set(val)
        return METRIC

    return instrumentation


@app.get("/healthcheck")
async def healthcheck():
    return 200

