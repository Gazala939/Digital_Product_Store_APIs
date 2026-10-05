from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Cart
from schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)
from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# REGISTER


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create an empty cart for the user
    new_cart = Cart(
        user_id=new_user.id
    )

    db.add(new_cart)
    db.commit()

    return new_user


# LOGIN
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    # Check user and password
    if not user or not verify_password(
        user_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token({
        "user_id": user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# PROFILE


@router.get(
    "/profile",
    response_model=UserResponse
)
def profile(
    current_user: User = Depends(get_current_user)
):

    return current_user