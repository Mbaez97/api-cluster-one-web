import logging

from brotli_middleware import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.gzip import GZipMiddleware, Headers, Receive, Scope, Send
from app.api.api_v1.api import api_router


logger = logging.getLogger("Autenticacion")
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT)

app = FastAPI()

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


app.include_router(api_router, prefix="/v1/api", tags=["api_v1"])
