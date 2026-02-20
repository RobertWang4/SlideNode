from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, user_id: str, auth0_sub: str):
        self.user_id = user_id
        self.auth0_sub = auth0_sub


def _extract_sub(token: str) -> str:
    try:
        claims = jwt.get_unverified_claims(token)
    except Exception:
        raise HTTPException(status_code=401, detail="AUTH_REQUIRED")
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="AUTH_REQUIRED")
    return sub


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if creds is None:
        if settings.auth0_skip_verify:
            sub = "dev|local-user"
        else:
            raise HTTPException(status_code=401, detail="AUTH_REQUIRED")
    elif settings.auth0_skip_verify:
        # Dev mode: use token as sub directly without JWT decoding
        sub = f"dev|{creds.credentials[:32]}" if creds.credentials else "dev|local-user"
    else:
        sub = _extract_sub(creds.credentials)
    user = db.query(User).filter(User.auth0_sub == sub).first()
    if not user:
        user = User(auth0_sub=sub)
        db.add(user)
        db.commit()
        db.refresh(user)

    return CurrentUser(str(user.id), sub)
