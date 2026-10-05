from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================================
# AUTHENTICATION SCHEMAS
# ============================================================

class UserRegister(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# PRODUCT SCHEMAS
# ============================================================

class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200
    )

    description: Optional[str] = None

    price: float = Field(
        gt=0
    )

    image: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200
    )

    description: Optional[str] = None

    price: Optional[float] = Field(
        default=None,
        gt=0
    )

    image: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    image: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProductListResponse(BaseModel):
    items: List[ProductResponse]

    page: int
    limit: int

    total: int
    total_pages: int


# ============================================================
# CART SCHEMAS
# ============================================================

class CartItemCreate(BaseModel):
    product_id: int

    quantity: int = Field(
        gt=0
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        gt=0
    )


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total_amount: float


# ============================================================
# ORDER SCHEMAS
# ============================================================

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_status: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: List[OrderResponse]

    page: int
    limit: int

    total: int
    total_pages: int


# ============================================================
# PAYMENT SCHEMAS
# ============================================================

class CheckoutResponse(BaseModel):
    checkout_url: str


# ============================================================
# ADMIN SCHEMAS
# ============================================================

class StatisticsResponse(BaseModel):
    total_products: int
    total_orders: int
    paid_orders: int
    revenue: float