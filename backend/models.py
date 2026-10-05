from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Text
)

from sqlalchemy.orm import relationship

from database import Base


# ============================================================
# USER
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="USER",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # One User → One Cart
    cart = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # One User → Many Orders
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ============================================================
# PRODUCT
# ============================================================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    price = Column(
        Float,
        nullable=False
    )

    image = Column(
        String(500),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Product → CartItems
    cart_items = relationship(
        "CartItem",
        back_populates="product"
    )

    # Product → OrderItems
    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )


# ============================================================
# CART
# ============================================================

class Cart(Base):

    __tablename__ = "carts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Cart → User
    user = relationship(
        "User",
        back_populates="cart"
    )

    # Cart → Many CartItems
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


# ============================================================
# CART ITEM
# ============================================================

class CartItem(Base):

    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    # CartItem → Cart
    cart = relationship(
        "Cart",
        back_populates="items"
    )

    # CartItem → Product
    product = relationship(
        "Product",
        back_populates="cart_items"
    )


# ============================================================
# ORDER
# ============================================================

class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(20),
        default="PENDING",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Order → User
    user = relationship(
        "User",
        back_populates="orders"
    )

    # Order → Many OrderItems
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # Order → One Payment
    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ============================================================
# ORDER ITEM
# ============================================================

class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    product_name = Column(
        String(200),
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    # OrderItem → Order
    order = relationship(
        "Order",
        back_populates="items"
    )

    # OrderItem → Product
    product = relationship(
        "Product",
        back_populates="order_items"
    )


# ============================================================
# PAYMENT
# ============================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        unique=True,
        nullable=False
    )

    stripe_session_id = Column(
        String(255),
        unique=True,
        nullable=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(20),
        default="PENDING",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Payment → Order
    order = relationship(
        "Order",
        back_populates="payment"
    )