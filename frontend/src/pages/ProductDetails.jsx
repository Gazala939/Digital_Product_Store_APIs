import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import api from "../api";
import Loading from "../components/Loading";

function ProductDetails() {
  const { productId } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  async function fetchProduct() {
    try {
      setLoading(true);

      const response = await api.get(
        `/products/${productId}`
      );

      setProduct(response.data);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Product not found"
      );

    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  async function handleAddToCart() {
    try {
      setAdding(true);

      await api.post("/cart/items", {
        product_id: Number(productId),
        quantity: quantity,
      });

      toast.success("Product added to cart!");

      navigate("/cart");

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to add product to cart"
      );

    } finally {
      setAdding(false);
    }
  }

  if (loading) {
    return <Loading />;
  }

  if (!product) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">
          Product not found.
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="max-w-5xl mx-auto px-6 py-10">

        <div className="bg-white rounded-xl shadow-lg overflow-hidden">

          <div className="md:flex">

            {/* Product Image */}
            <div className="md:w-1/2">

              {product.image ? (
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full h-96 object-cover"
                />
              ) : (
                <div className="w-full h-96 bg-gray-200 flex items-center justify-center">
                  <span className="text-gray-500">
                    No Image
                  </span>
                </div>
              )}

            </div>

            {/* Product Information */}
            <div className="md:w-1/2 p-8">

              <h1 className="text-3xl font-bold mb-4">
                {product.name}
              </h1>

              <p className="text-gray-600 mb-6">
                {product.description}
              </p>

              <p className="text-2xl font-bold mb-6">
                ₹{product.price}
              </p>

              {/* Quantity */}
              <div className="mb-6">

                <label className="block font-medium mb-2">
                  Quantity
                </label>

                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(
                      Math.max(
                        1,
                        Number(e.target.value)
                      )
                    )
                  }
                  className="w-24 border rounded-lg px-3 py-2"
                />

              </div>

              <button
                onClick={handleAddToCart}
                disabled={adding}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
              >
                {adding
                  ? "Adding..."
                  : "Add to Cart"}
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default ProductDetails;