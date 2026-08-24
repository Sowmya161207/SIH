from typing import List, Optional, Dict
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

security_scheme = HTTPBearer()

class User(BaseModel):
    username: str
    roles: List[str]
    workspace_id: str

# Mock user database for demonstration purposes
MOCK_USERS: Dict[str, User] = {
    "token_admin": User(
        username="admin_user", 
        roles=["Admin", "Manager", "Maintenance Engineer", "Operator", "Safety Officer"], 
        workspace_id="MRPL-HQ"
    ),
    "token_manager": User(
        username="manager_user", 
        roles=["Manager"], 
        workspace_id="MRPL-BLR"
    ),
    "token_operator": User(
        username="operator_user", 
        roles=["Operator"], 
        workspace_id="MRPL-BLR"
    ),
    "token_safety": User(
        username="safety_user", 
        roles=["Safety Officer"], 
        workspace_id="MRPL-BLR"
    ),
    "token_engineer": User(
        username="engineer_user", 
        roles=["Maintenance Engineer"], 
        workspace_id="MRPL-MUM"
    ),
}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    """Dependency to get the current authenticated user based on Bearer token."""
    token = credentials.credentials
    user = MOCK_USERS.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

class RoleChecker:
    """Dependency for Role-Based Access Control."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        # Admin bypass
        if "Admin" in user.roles:
            return user
            
        for role in user.roles:
            if role in self.allowed_roles:
                return user
                
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Required one of: {self.allowed_roles}"
        )
