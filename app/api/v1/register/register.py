import logging

from fastapi import APIRouter, Body, Form, HTTPException, Query
from tortoise.expressions import Q


from app.controllers.user import user_controller
from app.models.admin import User
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.users import CusUserCreate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/phone", summary="手机号码注册")
async def register_with_username(user_in: CusUserCreate):
    user = await user_controller.get_by_phone(user_in.phone)
    if user:
        return Fail(code=400, msg="The user with this phone already exists in the system.")
    user = await user_controller.get_by_phone(user_in.phone)
    new_user = await user_controller.create_user(obj_in=user_in)
    return {"message": "注册成功","user_id":f"{new_user.id}"}