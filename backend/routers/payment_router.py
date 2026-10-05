import stripe

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from database import get_db
from dependencies import get_current_user
from models import Cart, CartItem, Order, OrderItem, Payment, User
from schemas import CheckoutResponse


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = STRIPE_SECRET_KEY


# ============================================================
# CREATE STRIPE CHECKOUT SESSION
# ============================================================

@router.post(
    "/create-checkout-session",
    response_model=CheckoutResponse
)
def create_checkout_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Get current user's cart
    # --------------------------------------------------------

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # --------------------------------------------------------
    # Check products and calculate total
    # --------------------------------------------------------

    total_amount = 0

    for cart_item in cart.items:

        if not cart_item.product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Product '{cart_item.product.name}' "
                    "is no longer available"
                )
            )

        total_amount += (
            cart_item.product.price *
            cart_item.quantity
        )

    # --------------------------------------------------------
    # Create pending order
    # --------------------------------------------------------

    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="PENDING"
    )

    db.add(new_order)
    db.flush()

    # --------------------------------------------------------
    # Create order items
    # --------------------------------------------------------

    for cart_item in cart.items:

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            price=cart_item.product.price,
            quantity=cart_item.quantity
        )

        db.add(order_item)

    # --------------------------------------------------------
    # Create pending payment
    # --------------------------------------------------------

    payment = Payment(
        order_id=new_order.id,
        amount=total_amount,
        status="PENDING"
    )

    db.add(payment)
    db.flush()

    # --------------------------------------------------------
    # Create Stripe line items
    # --------------------------------------------------------

    line_items = []

    for cart_item in cart.items:

        line_items.append({
            "price_data": {
                "currency": "inr",
                "product_data": {
                    "name": cart_item.product.name
                },
                "unit_amount": int(
                    round(cart_item.product.price * 100)
                )
            },
            "quantity": cart_item.quantity
        })

    # --------------------------------------------------------
    # Create Stripe Checkout Session
    # --------------------------------------------------------

    try:

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,

            success_url=(
                "http://localhost:5173/orders"
                "?payment=success"
            ),

            cancel_url=(
                "http://localhost:5173/cart"
                "?payment=cancelled"
            ),

            metadata={
                "order_id": str(new_order.id)
            }
        )

    except stripe.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

    # --------------------------------------------------------
    # Save Stripe session ID
    # --------------------------------------------------------

    payment.stripe_session_id = checkout_session.id

    # --------------------------------------------------------
    # Clear cart
    # --------------------------------------------------------

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return {
        "checkout_url": checkout_session.url
    }


# ============================================================
# STRIPE WEBHOOK
# ============================================================

@router.post(
    "/webhook"
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Read raw Stripe request body
    # --------------------------------------------------------

    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )

    # --------------------------------------------------------
    # Validate Stripe webhook
    # --------------------------------------------------------

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload"
        )

    except stripe.SignatureVerificationError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )

    # --------------------------------------------------------
    # Get event type
    # --------------------------------------------------------

    event_type = event["type"]

    # ========================================================
    # SUCCESSFUL CHECKOUT
    # ========================================================

    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        order_id = session.get(
            "metadata",
            {}
        ).get("order_id")

        session_id = session.get("id")

        if order_id:

            order = db.query(Order).filter(
                Order.id == int(order_id)
            ).first()

            payment = db.query(Payment).filter(
                Payment.order_id == int(order_id)
            ).first()

            if order and payment:

                order.status = "PAID"

                payment.status = "PAID"

                payment.stripe_session_id = session_id

                db.commit()

    # ========================================================
    # FAILED PAYMENT
    # ========================================================

    elif event_type == "checkout.session.async_payment_failed":

        session = event["data"]["object"]

        order_id = session.get(
            "metadata",
            {}
        ).get("order_id")

        if order_id:

            order = db.query(Order).filter(
                Order.id == int(order_id)
            ).first()

            payment = db.query(Payment).filter(
                Payment.order_id == int(order_id)
            ).first()

            if order and payment:

                order.status = "FAILED"

                payment.status = "FAILED"

                db.commit()

    # ========================================================
    # EXPIRED CHECKOUT SESSION
    # ========================================================

    elif event_type == "checkout.session.expired":

        session = event["data"]["object"]

        order_id = session.get(
            "metadata",
            {}
        ).get("order_id")

        if order_id:

            order = db.query(Order).filter(
                Order.id == int(order_id)
            ).first()

            payment = db.query(Payment).filter(
                Payment.order_id == int(order_id)
            ).first()

            if order and payment:

                order.status = "CANCELLED"

                payment.status = "CANCELLED"

                db.commit()

    # --------------------------------------------------------
    # Return successful webhook response
    # --------------------------------------------------------

    return {
        "received": True
    }