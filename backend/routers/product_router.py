from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Product, User
from schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from dependencies import get_current_user, require_admin


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ============================================================
# CREATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        image=product_data.image
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ============================================================
# LIST PRODUCTS
# SEARCH + PAGINATION
# ============================================================

@router.get(
    "",
    response_model=ProductListResponse
)
def list_products(
    page: int = Query(
        1,
        ge=1
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100
    ),

    search: str = Query(
        "",
        max_length=100
    ),

    db: Session = Depends(get_db)
):

    query = db.query(Product).filter(
        Product.is_active == True
    )

    # Search by product name
    if search:
        query = query.filter(
            Product.name.ilike(
                f"%{search}%"
            )
        )

    # Total products
    total = query.count()

    # Calculate total pages
    total_pages = ceil(
        total / limit
    ) if total > 0 else 0

    # Pagination
    products = query.offset(
        (page - 1) * limit
    ).limit(
        limit
    ).all()

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


# ============================================================
# GET PRODUCT BY ID
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# ============================================================
# UPDATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Update only values that were provided
    update_data = product_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            product,
            field,
            value
        )

    db.commit()
    db.refresh(product)

    return product


# ============================================================
# SOFT DELETE PRODUCT
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Do not physically delete the product
    product.is_active = False

    db.commit()

    return {
        "message": "Product deleted successfully"
    }