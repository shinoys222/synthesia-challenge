from fastapi import APIRouter
from app.routers.crypto import sign_message

router = APIRouter(tags=["v1"])

router.get(
    "/crypto/sign",
    dependencies=[],
)(sign_message)
