import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import api from "../api";
import Loading from "../components/Loading";

function Cart() {
  const navigate = useNavigate();

  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [orderLoading, setOrderLoading] = useState(false);

  async function fetchCart() {
    try {
      setLoading(true);

      const response = await api.get("/cart");

      setCart(response.data);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load cart"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchCart();
  }, []);

  async function updateQuantity(itemId, quantity) {
    if (quantity < 1) {
      return;
    }

    try {
      const response = await api.put(
        `/cart/items/${itemId}`,
        {
          quantity: quantity,
        }
      );

      setCart(response.data);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to update quantity"
      );
    }
  }

  async function removeItem(itemId) {
    try {
      const response = await api.delete(
        `/cart/items/${itemId}`
      );

      setCart(response.data);

      toast.success("Item removed from cart");

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to remove item"
      );
    }
  }

  async function clearCart() {
    try {
      await api.delete("/cart");

      toast.success("Cart cleared");

      fetchCart();

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to clear cart"
      );
    }
  }

  // Place order without Stripe
  async function handlePlaceOrder() {
    try {
      setOrderLoading(true);

      await api.post("/orders");

      toast.success("Order placed successfully!");

      navigate("/orders");

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to place order"
      );
    } finally {
      setOrderLoading(false);
    }
  }

  // Stripe checkout
  async function handleCheckout() {
    try {
      setCheckoutLoading(true);

      const response = await api.post(
        "/payments/create-checkout-session"
      );

      window.location.href =
        response.data.checkout_url;

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Checkout failed"
      );
    } finally {
      setCheckoutLoading(false);
    }
  }

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="max-w-5xl mx-auto px-6 py-8">

        <h1 className="text-3xl font-bold mb-8">
          My Cart
        </h1>

        {!cart || cart.items.length === 0 ? (

          <div className="bg-white rounded-xl shadow p-10 text-center">

            <p className="text-xl text-gray-500 mb-6">
              Your cart is empty.
            </p>

            <button
              onClick={() => navigate("/products")}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              Browse Products
            </button>

          </div>

        ) : (

          <div className="space-y-6">

            {/* Cart Items */}

            <div className="bg-white rounded-xl shadow">

              {cart.items.map((item) => (

                <div
                  key={item.id}
                  className="border-b p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
                >

                  <div>

                    <h2 className="text-xl font-semibold">
                      {item.product_name}
                    </h2>

                    <p className="text-gray-500">
                      ₹{item.price} each
                    </p>

                    <p className="font-medium mt-2">
                      Subtotal: ₹{item.subtotal}
                    </p>

                  </div>

                  <div className="flex items-center gap-3">

                    {/* Decrease */}

                    <button
                      onClick={() =>
                        updateQuantity(
                          item.id,
                          item.quantity - 1
                        )
                      }
                      disabled={item.quantity === 1}
                      className="w-9 h-9 border rounded-lg disabled:opacity-40"
                    >
                      -
                    </button>

                    {/* Quantity */}

                    <span className="font-semibold">
                      {item.quantity}
                    </span>

                    {/* Increase */}

                    <button
                      onClick={() =>
                        updateQuantity(
                          item.id,
                          item.quantity + 1
                        )
                      }
                      className="w-9 h-9 border rounded-lg"
                    >
                      +
                    </button>

                    {/* Remove */}

                    <button
                      onClick={() =>
                        removeItem(item.id)
                      }
                      className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
                    >
                      Remove
                    </button>

                  </div>

                </div>

              ))}

            </div>

            {/* Cart Total */}

            <div className="bg-white rounded-xl shadow p-6">

              <div className="flex justify-between text-2xl font-bold mb-6">
                <span>Total</span>

                <span>
                  ₹{cart.total_amount}
                </span>
              </div>

              <div className="flex flex-col md:flex-row gap-4">

                {/* Clear Cart */}

                <button
                  onClick={clearCart}
                  className="flex-1 border border-red-500 text-red-500 py-3 rounded-lg hover:bg-red-50"
                >
                  Clear Cart
                </button>

                {/* Place Normal Order */}

                <button
                  onClick={handlePlaceOrder}
                  disabled={orderLoading}
                  className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {orderLoading
                    ? "Placing Order..."
                    : "Place Order"}
                </button>

                {/* Stripe Checkout */}

                <button
                  onClick={handleCheckout}
                  disabled={checkoutLoading}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50"
                >
                  {checkoutLoading
                    ? "Processing..."
                    : "Stripe Checkout"}
                </button>

              </div>

            </div>

          </div>

        )}

      </div>

    </div>
  );
}

export default Cart;