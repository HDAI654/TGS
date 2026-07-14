from fastapi import APIRouter

from src.modules.auth.presentation.api.v1 import (
    signup,
    login,
    logout,
    send_verification,
    del_account,
    revoke,
    revoke_all_other,
    set_password,
    token_rotation,
    forget_pass_verify,
    reset_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

router.include_router(signup.router)
router.include_router(login.router)
router.include_router(logout.router)
router.include_router(send_verification.router)
router.include_router(del_account.router)
router.include_router(revoke.router)
router.include_router(revoke_all_other.router)
router.include_router(set_password.router)
router.include_router(token_rotation.router)
router.include_router(forget_pass_verify.router)
router.include_router(reset_password.router)
