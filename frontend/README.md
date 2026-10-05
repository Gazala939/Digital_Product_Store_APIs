# Digital Product Store

A full-stack digital product e-commerce application built using **FastAPI, React.js, SQLAlchemy, SQLite, JWT authentication, and Stripe integration**.

## Project Overview

Digital Product Store allows users to:

* Register and login
* Browse digital products
* Search products
* View product details
* Add products to cart
* Update cart quantities
* Remove products from cart
* Place orders
* View their orders
* Make payments using Stripe checkout

Administrators can:

* Add products
* Edit products
* Delete products using soft delete
* View all products
* View all orders
* View store statistics
* View revenue and purchase reports

---

## Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* JWT Authentication
* Argon2 Password Hashing
* Stripe
* Pytest

### Frontend

* React.js
* Vite
* Axios
* React Router
* React Toastify
* Tailwind CSS

---




# Backend Setup

Open Command Prompt.

Go to the backend folder:

```cmd
cd C:\Digital_Product_Store\backend
```

Create a virtual environment:

```cmd
python -m venv venv
```

Activate it:

```cmd
venv\Scripts\activate
```

Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside the `backend` folder.

Example:

```env
DATABASE_URL=sqlite:///./store.db
SECRET_KEY=my-super-secret-key-for-digital-store
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

Do not commit real Stripe secret keys to GitHub.

---

# Create Admin User

From the backend folder:

```cmd
python create_admin.py
```

Default local demo credentials:

```text
Email: admin@example.com
Password: admin123
```

---

# Run Backend

From:

```text
C:\Digital_Product_Store\backend
```

Run:

```cmd
python -m uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

# Backend API Endpoints

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/profile
```

## Products

```text
POST   /products
GET    /products
GET    /products/{product_id}
PUT    /products/{product_id}
DELETE /products/{product_id}
```

Product listing supports:

* Search
* Pagination

Example:

```text
/products?page=1&limit=10&search=python
```

---

## Cart

```text
GET    /cart
POST   /cart/items
PUT    /cart/items/{item_id}
DELETE /cart/items/{item_id}
DELETE /cart
```

---

## Orders

```text
POST /orders
GET  /orders
GET  /orders/{order_id}
```

---

## Payments

```text
POST /payments/create-checkout-session
POST /payments/webhook
```

Payment statuses include:

```text
PENDING
PAID
FAILED
CANCELLED
```

Payment status is updated through the Stripe webhook.

---

## Admin

```text
GET    /admin/products
DELETE /admin/products/{product_id}

GET /admin/orders
GET /admin/statistics

GET /admin/reports/revenue
GET /admin/reports/most-purchased
GET /admin/reports/user-orders
```

Admin product creation and updating are handled through the main product APIs with admin authorization.

---

# Frontend Setup

Open a second Command Prompt.

Go to:

```cmd
cd C:\Digital_Product_Store\frontend
```

Install dependencies:

```cmd
npm install
```

Run the frontend:

```cmd
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

# Frontend Pages

The application includes:

```text
/login
/register
/products
/products/:id
/cart
/orders
/admin/products
/admin/orders
```

---

# Authentication

JWT authentication is used to protect private APIs.

The frontend stores the JWT token and automatically sends it with protected API requests using Axios.

Admin pages are protected using the user's role.

---

# Database Relationships

The application uses the following relationships:

```text
User
 ├── Cart
 └── Orders

Cart
 └── CartItems

Product
 ├── CartItems
 └── OrderItems

Order
 ├── OrderItems
 └── Payment
```

---

# Testing

The backend contains meaningful Pytest tests covering:

* User registration
* Login
* Invalid login
* Product listing
* Product creation
* Cart operations
* Order creation
* Unauthorized product creation
* User profile
* Empty cart order validation

Run tests using:

```cmd
cd C:\Digital_Product_Store\backend
venv\Scripts\activate
python -m pytest -v
```

Current result:

```text
10 passed
```

---

# Stripe

Stripe checkout and webhook integration are implemented using Stripe test-mode architecture.

The application supports:

* Checkout session creation
* Successful payment handling
* Failed payment handling
* Cancelled/expired checkout handling
* Payment status updates through webhook events

Live Stripe checkout requires valid Stripe account credentials and webhook configuration.

---

# Validation and Error Handling

The application includes:

* Pydantic validation
* JWT authentication
* Role-based authorization
* Duplicate email validation
* Product availability validation
* Cart validation
* Empty cart validation
* Order ownership validation
* HTTP error responses
* Protected admin APIs

---

# Features Summary

### User

* Registration
* Login
* JWT authentication
* Profile
* Product search
* Product pagination
* Product details
* Cart management
* Order creation
* Order history

### Admin

* Product management
* Soft delete products
* Order management
* Store statistics
* Revenue report
* Most purchased products report
* User order report

### Payment

* Stripe checkout
* Webhook handling
* Payment status tracking

---

# Project Status

The Digital Product Store application is completed as a full-stack assignment with:

* FastAPI backend
* React frontend
* Database persistence
* Authentication and authorization
* Product management
* Cart management
* Order management
* Payment integration
* Admin dashboard
* SQL reports
* Automated tests

**Backend tests: 10/10 passed.**

Stripe checkout and webhook integration have been implemented using Stripe test-mode APIs. Live Stripe credentials are not included in the project. Actual payment testing requires Stripe account access and credentials.

.env contains empty placeholders rather than any secret key:
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=