from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from google_sheets_api import (
    subscribe,
    unsubscribe,
    check_subscriber,
)


router = APIRouter()


class SubscribeRequest(BaseModel):
    email: EmailStr


class CheckSubscriberRequest(BaseModel):
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


@router.post("/check-subscriber")
def check_subscriber_user(
    request: CheckSubscriberRequest
):
    result = check_subscriber(
        str(request.email)
    )

    return result