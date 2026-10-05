import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();

  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");

    navigate("/login");
  }

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex justify-between items-center">
      
      <Link
        to="/products"
        className="text-xl font-bold"
      >
        Digital Product Store
      </Link>

      {token && (
        <div className="flex items-center gap-5">

          <Link
            to="/products"
            className="hover:text-gray-300"
          >
            Products
          </Link>

          <Link
            to="/cart"
            className="hover:text-gray-300"
          >
            Cart
          </Link>

          <Link
            to="/orders"
            className="hover:text-gray-300"
          >
            Orders
          </Link>

          {role === "ADMIN" && (
            <>
              <Link
                to="/admin/products"
                className="hover:text-gray-300"
              >
                Admin Products
              </Link>

              <Link
                to="/admin/orders"
                className="hover:text-gray-300"
              >
                Admin Orders
              </Link>
            </>
          )}

          <button
            onClick={logout}
            className="bg-red-500 px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>

        </div>
      )}
    </nav>
  );
}

export default Navbar;