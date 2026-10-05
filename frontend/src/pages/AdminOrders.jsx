import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import api from "../api";
import Loading from "../components/Loading";

function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  async function fetchOrders() {
    try {
      setLoading(true);

      const response = await api.get("/admin/orders", {
        params: {
          page: 1,
          limit: 20,
        },
      });

      setOrders(response.data.items);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load orders"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOrders();
  }, []);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="max-w-7xl mx-auto px-6 py-8">

        <h1 className="text-3xl font-bold mb-8">
          Admin - Orders
        </h1>

        {orders.length === 0 ? (

          <div className="bg-white rounded-xl shadow p-10 text-center">

            <p className="text-xl text-gray-500">
              No orders available.
            </p>

          </div>

        ) : (

          <div className="space-y-6">

            {orders.map((order) => (

              <div
                key={order.id}
                className="bg-white rounded-xl shadow p-6"
              >

                {/* Order Header */}
                <div className="flex flex-col md:flex-row md:justify-between gap-4 mb-5">

                  <div>

                    <h2 className="text-xl font-bold">
                      Order #{order.id}
                    </h2>

                    <p className="text-gray-500">
                      User ID: {order.user_id}
                    </p>

                    <p className="text-gray-500">
                      {new Date(
                        order.created_at
                      ).toLocaleString()}
                    </p>

                  </div>

                  <div className="text-left md:text-right">

                    <p className="text-xl font-bold">
                      ₹{order.total_amount}
                    </p>

                    <p>
                      Order Status:{" "}
                      <span className="font-semibold">
                        {order.status}
                      </span>
                    </p>

                    <p>
                      Payment:{" "}
                      <span className="font-semibold">
                        {order.payment_status || "PENDING"}
                      </span>
                    </p>

                  </div>

                </div>

                {/* Order Items */}
                <div className="border-t pt-4">

                  <h3 className="font-semibold mb-3">
                    Products
                  </h3>

                  <div className="space-y-3">

                    {order.items.map((item) => (

                      <div
                        key={item.id}
                        className="flex justify-between items-center border-b pb-3"
                      >

                        <div>

                          <p className="font-medium">
                            {item.product_name}
                          </p>

                          <p className="text-gray-500">
                            ₹{item.price} ×{" "}
                            {item.quantity}
                          </p>

                        </div>

                        <p className="font-semibold">
                          ₹
                          {item.price *
                            item.quantity}
                        </p>

                      </div>

                    ))}

                  </div>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>
  );
}

export default AdminOrders;