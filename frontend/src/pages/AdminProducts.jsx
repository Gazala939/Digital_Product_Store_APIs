
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import api from "../api";
import Loading from "../components/Loading";

function AdminProducts() {
  const [products, setProducts] = useState([]);

  const [statistics, setStatistics] = useState({
    total_products: 0,
    total_orders: 0,
    paid_orders: 0,
    revenue: 0,
  });

  const [revenueReport, setRevenueReport] = useState([]);
  const [mostPurchasedReport, setMostPurchasedReport] = useState([]);
  const [userOrdersReport, setUserOrdersReport] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState("");

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // --------------------------------------------------
  // Get products
  // --------------------------------------------------

  async function fetchProducts() {
    try {
      const response = await api.get(
        "/admin/products"
      );

      setProducts(response.data);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load products"
      );
    }
  }

  // --------------------------------------------------
  // Get statistics
  // --------------------------------------------------

  async function fetchStatistics() {
    try {
      const response = await api.get(
        "/admin/statistics"
      );

      setStatistics(response.data);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load statistics"
      );
    }
  }

  // --------------------------------------------------
  // Get reports
  // --------------------------------------------------

  async function fetchReports() {
    try {
      const [
        revenueResponse,
        mostPurchasedResponse,
        userOrdersResponse,
      ] = await Promise.all([
        api.get("/admin/reports/revenue"),
        api.get("/admin/reports/most-purchased"),
        api.get("/admin/reports/user-orders"),
      ]);

      setRevenueReport(
        Array.isArray(revenueResponse.data)
          ? revenueResponse.data
          : []
      );

      setMostPurchasedReport(
        Array.isArray(mostPurchasedResponse.data)
          ? mostPurchasedResponse.data
          : []
      );

      setUserOrdersReport(
        Array.isArray(userOrdersResponse.data)
          ? userOrdersResponse.data
          : []
      );

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load reports"
      );
    }
  }

  // --------------------------------------------------
  // Load admin data
  // --------------------------------------------------

  async function loadAdminData() {
    try {
      setLoading(true);

      await Promise.all([
        fetchProducts(),
        fetchStatistics(),
        fetchReports(),
      ]);

    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAdminData();
  }, []);

  // --------------------------------------------------
  // Create / Update Product
  // --------------------------------------------------

  async function handleSubmit(e) {
    e.preventDefault();

    if (!name || !price) {
      toast.error(
        "Product name and price are required"
      );
      return;
    }

    try {
      setSaving(true);

      const productData = {
        name: name,
        description: description || null,
        price: Number(price),
        image: image || null,
      };

      // Update existing product
      if (editingId) {

        await api.put(
          `/products/${editingId}`,
          productData
        );

        toast.success(
          "Product updated successfully"
        );

      } else {

        // Create new product
        await api.post(
          "/products",
          productData
        );

        toast.success(
          "Product created successfully"
        );
      }

      clearForm();

      await fetchProducts();
      await fetchStatistics();
      await fetchReports();

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to save product"
      );
    } finally {
      setSaving(false);
    }
  }

  // --------------------------------------------------
  // Start editing
  // --------------------------------------------------

  function editProduct(product) {
    setEditingId(product.id);

    setName(product.name);
    setDescription(
      product.description || ""
    );
    setPrice(product.price);
    setImage(
      product.image || ""
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  // --------------------------------------------------
  // Clear form
  // --------------------------------------------------

  function clearForm() {
    setEditingId(null);
    setName("");
    setDescription("");
    setPrice("");
    setImage("");
  }

  // --------------------------------------------------
  // Delete product
  // --------------------------------------------------

  async function deleteProduct(productId) {
    try {
      await api.delete(
        `/admin/products/${productId}`
      );

      toast.success(
        "Product deleted successfully"
      );

      await fetchProducts();
      await fetchStatistics();
      await fetchReports();

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to delete product"
      );
    }
  }

  // --------------------------------------------------
  // Loading
  // --------------------------------------------------

  if (loading) {
    return <Loading />;
  }

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* ==========================================
            ADMIN DASHBOARD
        ========================================== */}

        <h1 className="text-3xl font-bold mb-8">
          Admin Dashboard
        </h1>

        {/* Statistics */}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">

          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500">
              Total Products
            </p>

            <h2 className="text-3xl font-bold mt-2">
              {statistics.total_products}
            </h2>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500">
              Total Orders
            </p>

            <h2 className="text-3xl font-bold mt-2">
              {statistics.total_orders}
            </h2>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500">
              Paid Orders
            </p>

            <h2 className="text-3xl font-bold mt-2">
              {statistics.paid_orders}
            </h2>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500">
              Revenue
            </p>

            <h2 className="text-3xl font-bold mt-2">
              ₹{statistics.revenue}
            </h2>
          </div>

        </div>

        {/* ==========================================
            CREATE / UPDATE PRODUCT
        ========================================== */}

        <div className="bg-white rounded-xl shadow p-6 mb-8">

          <h2 className="text-2xl font-semibold mb-5">

            {editingId
              ? "Edit Product"
              : "Add New Product"}

          </h2>

          <form
            onSubmit={handleSubmit}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >

            {/* Product Name */}

            <input
              type="text"
              placeholder="Product name"
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
              className="border rounded-lg px-4 py-3"
            />

            {/* Price */}

            <input
              type="number"
              placeholder="Price"
              min="1"
              value={price}
              onChange={(e) =>
                setPrice(e.target.value)
              }
              className="border rounded-lg px-4 py-3"
            />

            {/* Description */}

            <textarea
              placeholder="Description"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
              className="border rounded-lg px-4 py-3 md:col-span-2"
              rows="3"
            />

            {/* Image */}

            <input
              type="text"
              placeholder="Image URL"
              value={image}
              onChange={(e) =>
                setImage(e.target.value)
              }
              className="border rounded-lg px-4 py-3"
            />

            {/* Submit */}

            <button
              type="submit"
              disabled={saving}
              className="bg-blue-600 text-white rounded-lg px-5 py-3 font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : editingId
                ? "Update Product"
                : "Create Product"}
            </button>

            {/* Cancel */}

            {editingId && (

              <button
                type="button"
                onClick={clearForm}
                className="border border-gray-400 text-gray-700 rounded-lg px-5 py-3 font-semibold hover:bg-gray-100 md:col-span-2"
              >
                Cancel Edit
              </button>

            )}

          </form>

        </div>

        {/* ==========================================
            ALL PRODUCTS
        ========================================== */}

        <div className="bg-white rounded-xl shadow overflow-hidden mb-10">

          <div className="p-6 border-b">

            <h2 className="text-2xl font-semibold">
              All Products
            </h2>

          </div>

          {products.length === 0 ? (

            <p className="p-6 text-gray-500">
              No products available.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead className="bg-gray-100">

                  <tr>

                    <th className="text-left p-4">
                      ID
                    </th>

                    <th className="text-left p-4">
                      Name
                    </th>

                    <th className="text-left p-4">
                      Price
                    </th>

                    <th className="text-left p-4">
                      Status
                    </th>

                    <th className="text-left p-4">
                      Action
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {products.map((product) => (

                    <tr
                      key={product.id}
                      className="border-t"
                    >

                      <td className="p-4">
                        {product.id}
                      </td>

                      <td className="p-4 font-medium">
                        {product.name}
                      </td>

                      <td className="p-4">
                        ₹{product.price}
                      </td>

                      <td className="p-4">

                        {product.is_active
                          ? "Active"
                          : "Inactive"}

                      </td>

                      <td className="p-4 flex gap-2">

                        {/* Edit */}

                        {product.is_active && (

                          <button
                            onClick={() =>
                              editProduct(product)
                            }
                            className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600"
                          >
                            Edit
                          </button>

                        )}

                        {/* Delete */}

                        {product.is_active && (

                          <button
                            onClick={() =>
                              deleteProduct(
                                product.id
                              )
                            }
                            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
                          >
                            Delete
                          </button>

                        )}

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>

        {/* ==========================================
            ADMIN REPORTS
        ========================================== */}

        <h2 className="text-3xl font-bold mb-6">
          Admin Reports
        </h2>

        {/* Revenue Report */}

        <div className="bg-white rounded-xl shadow p-6 mb-6">

          <h3 className="text-xl font-semibold mb-4">
            Revenue Report
          </h3>

          {revenueReport.length === 0 ? (

            <p className="text-gray-500">
              No revenue data available.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead className="bg-gray-100">

                  <tr>

                    <th className="text-left p-4">
                      Date
                    </th>

                    <th className="text-left p-4">
                      Revenue
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {revenueReport.map(
                    (report, index) => (

                      <tr
                        key={index}
                        className="border-t"
                      >

                        <td className="p-4">
                          {report.date ||
                            report.order_date ||
                            "-"}
                        </td>

                        <td className="p-4 font-semibold">
                          ₹
                          {report.revenue ??
                            report.total_revenue ??
                            0}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </div>

        {/* Most Purchased */}

        <div className="bg-white rounded-xl shadow p-6 mb-6">

          <h3 className="text-xl font-semibold mb-4">
            Most Purchased Products
          </h3>

          {mostPurchasedReport.length === 0 ? (

            <p className="text-gray-500">
              No purchase data available.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead className="bg-gray-100">

                  <tr>

                    <th className="text-left p-4">
                      Product
                    </th>

                    <th className="text-left p-4">
                      Quantity Purchased
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {mostPurchasedReport.map(
                    (report, index) => (

                      <tr
                        key={index}
                        className="border-t"
                      >

                        <td className="p-4">
                          {report.product_name ||
                            report.name ||
                            "-"}
                        </td>

                        <td className="p-4 font-semibold">
                          {report.total_quantity ??
                            report.quantity ??
                            0}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </div>

        {/* User Orders */}

        <div className="bg-white rounded-xl shadow p-6 mb-10">

          <h3 className="text-xl font-semibold mb-4">
            User Orders Report
          </h3>

          {userOrdersReport.length === 0 ? (

            <p className="text-gray-500">
              No user order data available.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead className="bg-gray-100">

                  <tr>

                    <th className="text-left p-4">
                      User ID
                    </th>

                    <th className="text-left p-4">
                      Total Orders
                    </th>

                    <th className="text-left p-4">
                      Total Amount
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {userOrdersReport.map(
                    (report, index) => (

                      <tr
                        key={index}
                        className="border-t"
                      >

                        <td className="p-4">
                          {report.user_id}
                        </td>

                        <td className="p-4">
                          {report.total_orders ??
                            report.order_count ??
                            0}
                        </td>

                        <td className="p-4 font-semibold">
                          ₹
                          {report.total_amount ??
                            report.total_spent ??
                            0}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>

    </div>
  );
}

export default AdminProducts;

