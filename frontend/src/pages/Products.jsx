import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import api from "../api";
import ProductCard from "../components/ProductCard";
import Loading from "../components/Loading";

function Products() {
  const [products, setProducts] = useState([]);

  const [page, setPage] = useState(1);
  const [limit] = useState(6);

  const [totalPages, setTotalPages] = useState(0);

  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const [loading, setLoading] = useState(true);

  async function fetchProducts() {
    try {
      setLoading(true);

      const response = await api.get("/products", {
        params: {
          page: page,
          limit: limit,
          search: search,
        },
      });

      setProducts(response.data.items);
      setTotalPages(response.data.total_pages);

    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
        "Failed to load products"
      );

    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchProducts();
  }, [page, search]);

  function handleSearch(e) {
    e.preventDefault();

    setPage(1);
    setSearch(searchInput);
  }

  function previousPage() {
    if (page > 1) {
      setPage(page - 1);
    }
  }

  function nextPage() {
    if (page < totalPages) {
      setPage(page + 1);
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="max-w-7xl mx-auto px-6 py-8">

        <h1 className="text-3xl font-bold mb-6">
          Digital Products
        </h1>

        {/* Search */}
        <form
          onSubmit={handleSearch}
          className="flex gap-3 mb-8"
        >

          <input
            type="text"
            value={searchInput}
            onChange={(e) =>
              setSearchInput(e.target.value)
            }
            placeholder="Search products..."
            className="flex-1 border rounded-lg px-4 py-3 bg-white"
          />

          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Search
          </button>

        </form>

        {/* Products */}
        {loading ? (
          <Loading />
        ) : products.length === 0 ? (

          <div className="text-center py-10">
            <p className="text-gray-500 text-lg">
              No products found.
            </p>
          </div>

        ) : (

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
              />
            ))}

          </div>
        )}

        {/* Pagination */}
        {!loading && totalPages > 0 && (

          <div className="flex justify-center items-center gap-2 mt-10">

            <button
              onClick={previousPage}
              disabled={page === 1}
              className="px-4 py-2 border rounded-lg bg-white disabled:opacity-40"
            >
              Previous
            </button>

            {Array.from(
              { length: totalPages },
              (_, index) => index + 1
            ).map((pageNumber) => (

              <button
                key={pageNumber}
                onClick={() => setPage(pageNumber)}
                className={`px-4 py-2 rounded-lg ${
                  page === pageNumber
                    ? "bg-blue-600 text-white"
                    : "bg-white border"
                }`}
              >
                {pageNumber}
              </button>

            ))}

            <button
              onClick={nextPage}
              disabled={page === totalPages}
              className="px-4 py-2 border rounded-lg bg-white disabled:opacity-40"
            >
              Next
            </button>

          </div>
        )}

      </div>

    </div>
  );
}

export default Products;