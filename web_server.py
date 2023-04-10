import logging

from brotli_middleware import BrotliMiddleware
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic.schema import date
from starlette.middleware.gzip import GZipMiddleware, Headers, Receive, Scope, Send


logger = logging.getLogger("Autenticacion")
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GZipIfNotBrotli(GZipMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            if "br" not in headers.get("Accept-Encoding", ""):
                await super().__call__(scope, receive, send)
                return
        await self.app(scope, receive, send)


app.add_middleware(BrotliMiddleware, quality=9, minimum_size=400)
app.add_middleware(GZipIfNotBrotli, minimum_size=400)


@app.get("/", response_class=ORJSONResponse)
async def test_root():
    return {"Hello": "current_user.full_name"}


# app.include_router(router_v2_dashboard, prefix="/v2/dashboard", tags=["v2_dashboard"])
