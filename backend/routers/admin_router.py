from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_admin

from models import (
    User,
    Product,
    Order,
    OrderItem,
    Payment
)

from schemas import (
    ProductResponse,
    OrderListResponse,
    StatisticsResponse
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)



# ADMIN — VIEW ALL PRODUCTS
@router.get(
    "/products",
    response_model=list[ProductResponse]
)
def admin_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    products = db.query(Product).all()

    return products


# ADMIN — DELETE PRODUCT
@router.delete(
    "/products/{product_id}"
)
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Soft delete
    product.is_active = False

    db.commit()

    return {
        "message": "Product deleted successfully"
    }


# ADMIN — VIEW ALL ORDERS
@router.get(
    "/orders",
    response_model=OrderListResponse
)
def admin_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    query = db.query(Order)

    total = query.count()

    total_pages = (
        ceil(total / limit)
        if total > 0
        else 0
    )

    orders = query.order_by(
        Order.created_at.desc()
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()

    result = []

    for order in orders:

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

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_status": payment_status,
            "created_at": order.created_at,
            "items": items
        })

    return {
        "items": result,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


# ADMIN — STATISTICS
@router.get(
    "/statistics",
    response_model=StatisticsResponse
)
def statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    # Count only active products
    total_products = db.query(
        Product
    ).filter(
        Product.is_active == True
    ).count()

    # Count all orders
    total_orders = db.query(
        Order
    ).count()

    # Count paid orders
    paid_orders = db.query(
        Order
    ).filter(
        Order.status == "PAID"
    ).count()

    # Calculate revenue from paid payments
    revenue = db.query(
        func.coalesce(
            func.sum(Payment.amount),
            0
        )
    ).filter(
        Payment.status == "PAID"
    ).scalar()

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "revenue": float(revenue)
    }


# REPORT 1 — REVENUE
@router.get(
    "/reports/revenue"
)
def revenue_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    revenue = db.query(
        func.coalesce(
            func.sum(Payment.amount),
            0
        )
    ).filter(
        Payment.status == "PAID"
    ).scalar()

    return {
        "total_revenue": float(revenue)
    }


# REPORT 2 — MOST PURCHASED PRODUCTS
@router.get(
    "/reports/most-purchased"
)
def most_purchased_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    results = db.query(
        Product.id,
        Product.name,
        func.sum(
            OrderItem.quantity
        ).label("total_quantity")
    ).join(
        OrderItem,
        Product.id == OrderItem.product_id
    ).join(
        Order,
        Order.id == OrderItem.order_id
    ).filter(
        Order.status == "PAID"
    ).group_by(
        Product.id,
        Product.name
    ).order_by(
        func.sum(
            OrderItem.quantity
        ).desc()
    ).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "total_quantity": row.total_quantity
        }
        for row in results
    ]



# REPORT 3 — USER ORDER HISTORY
@router.get(
    "/reports/user-orders"
)
def user_order_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    results = db.query(
        User.id,
        User.name,
        User.email,

        func.count(
            Order.id
        ).label("total_orders"),

        func.coalesce(
            func.sum(Order.total_amount),
            0
        ).label("total_spent")

    ).join(
        Order,
        User.id == Order.user_id
    ).filter(
        # Only count completed/paid orders
        Order.status == "PAID"
    ).group_by(
        User.id,
        User.name,
        User.email
    ).order_by(
        func.count(Order.id).desc()
    ).all()

    return [
        {
            "user_id": row.id,
            "name": row.name,
            "email": row.email,
            "total_orders": row.total_orders,
            "total_spent": float(row.total_spent)
        }
        for row in results
    ]