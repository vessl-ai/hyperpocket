from fastapi import APIRouter

from hyperpocket.util.get_objects_from_subpackage import get_objects_from_subpackage

auth_router = APIRouter(prefix="/auth")

routers = get_objects_from_subpackage("hyperpocket.server.auth", APIRouter)
for r in routers:
    auth_router.include_router(r)
