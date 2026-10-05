import { Link } from "react-router-dom";

function ProductCard({ product }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border">

      {product.image ? (
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
          <span className="text-gray-500">
            No Image
          </span>
        </div>
      )}

      <div className="p-5">

        <h2 className="text-xl font-semibold mb-2">
          {product.name}
        </h2>

        <p className="text-gray-600 mb-3">
          {product.description}
        </p>

        <p className="text-lg font-bold mb-4">
          ₹{product.price}
        </p>

        <Link
          to={`/products/${product.id}`}
          className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          View Details
        </Link>

      </div>

    </div>
  );
}

export default ProductCard;