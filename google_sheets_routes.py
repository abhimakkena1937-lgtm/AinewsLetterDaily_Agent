from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from google_sheets_api import subscribe, unsubscribe


router = APIRouter()


class SubscribeRequest(BaseModel):
    email: EmailStr


@router.post("/subscribe")
def subscribe_user(request: SubscribeRequest):
    result = subscribe(str(request.email))

    return {
        "message": result.get(
            "message",
            "Successfully subscribed"
        )
    }


@router.post("/unsubscribe")
def unsubscribe_user(request: SubscribeRequest):
    result = unsubscribe(str(request.email))

    return {
        "message": result.get(
            "message",
            "Successfully unsubscribed"
        )
    }