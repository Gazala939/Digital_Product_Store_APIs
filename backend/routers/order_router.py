from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Cart, CartItem, Order, OrderItem, Payment, User
from schemas import OrderResponse, OrderListResponse
from dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ============================================================
# HELPER — CONVERT ORDER TO RESPONSE
# ============================================================

def build_order_response(order: Order):

    payment_status = None

    if order.payment:
        payment_status = order.payment.status

    items = []

    for item in order.items:
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "price": item.price,
            "quantity": item.quantity
        })

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_status": payment_status,
        "created_at": order.created_at,
        "items": items
    }


# ============================================================
# CREATE ORDER FROM CART
# ============================================================

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find user's cart
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    total_amount = 0

    # Calculate total
    for cart_item in cart.items:

        if not cart_item.product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{cart_item.product.name}' is no longer available"
            )

        total_amount += (
            cart_item.product.price *
            cart_item.quantity
        )

    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="PENDING"
    )

    db.add(new_order)
    db.flush()

    # Copy cart items into order items
    for cart_item in cart.items:

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            price=cart_item.product.price,
            quantity=cart_item.quantity
        )

        db.add(order_item)

    # Create payment record
    payment = Payment(
        order_id=new_order.id,
        amount=total_amount,
        status="PENDING"
    )

    db.add(payment)

    # Clear cart
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.commit()
    db.refresh(new_order)

    return build_order_response(new_order)


# ============================================================
# LIST MY ORDERS
# ============================================================

@router.get(
    "",
    response_model=OrderListResponse
)
def list_my_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Order).filter(
        Order.user_id == current_user.id
    )

    total = query.count()

    total_pages = ceil(
        total / limit
    ) if total > 0 else 0

    orders = query.order_by(
        Order.created_at.desc()
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()

    return {
        "items": [
            build_order_response(order)
            for order in orders
        ],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


# ============================================================
# GET SINGLE ORDER
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return build_order_response(order)