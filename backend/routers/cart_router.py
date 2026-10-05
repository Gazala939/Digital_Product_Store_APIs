from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Cart, CartItem, Product, User
from schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse
)
from dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)



# GET USER CART
def get_user_cart(
    current_user: User,
    db: Session
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        cart = Cart(
            user_id=current_user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart



# VIEW CART
@router.get(
    "",
    response_model=CartResponse
)
def view_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = get_user_cart(
        current_user,
        db
    )

    items = []
    total_amount = 0

    for item in cart.items:

        subtotal = (
            item.product.price *
            item.quantity
        )

        total_amount += subtotal

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return {
        "id": cart.id,
        "items": items,
        "total_amount": total_amount
    }



# ADD ITEM TO CART


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = get_user_cart(
        current_user,
        db
    )

    # Find active product
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check whether product already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    if existing_item:

        existing_item.quantity += item_data.quantity

    else:

        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=item_data.quantity
        )

        db.add(new_item)

    db.commit()

    return view_cart(
        db=db,
        current_user=current_user
    )



# UPDATE CART ITEM
@router.put(
    "/items/{item_id}",
    response_model=CartResponse
)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = get_user_cart(
        current_user,
        db
    )

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    item.quantity = item_data.quantity

    db.commit()

    return view_cart(
        db=db,
        current_user=current_user
    )

# REMOVE CART ITEM
@router.delete(
    "/items/{item_id}",
    response_model=CartResponse
)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = get_user_cart(
        current_user,
        db
    )

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    return view_cart(
        db=db,
        current_user=current_user
    )



# CLEAR CART

@router.delete(
    "",
    status_code=status.HTTP_200_OK
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = get_user_cart(
        current_user,
        db
    )

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }