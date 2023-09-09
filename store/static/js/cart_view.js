document.addEventListener("DOMContentLoaded", function () {
  const removeButtons = document.querySelectorAll(".remove-from-cart-btn");
  removeButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const productId = btn.getAttribute("data-product-id");
      removeFromCart(productId);
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const payBtn = document.querySelector(".auth-button");
  const modal = document.getElementById("loginModal");
  const closeBtn = document.querySelector(".close-btn");

  payBtn.addEventListener("click", function (event) {
    console.log("Pay button clicked");
    if (!isUserAuthenticated) {
      event.preventDefault(); // Prevent the button default behavior.
      modal.style.display = "block"; // Show the modal.
    }
  });

  closeBtn.addEventListener("click", function () {
    modal.style.display = "none"; // Close the modal.
  });

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none"; // Close the modal if clicked outside.
    }
  };
});

function removeFromCart(productId) {
  fetch(removeFromCartUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: JSON.stringify({
      product_id: productId,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Remove the product from the list
        const productElem = document.querySelector(`[data-product-id="${productId}"]`).closest(".collection-item");
        productElem.remove();

        // Update total price
        const totalElem = document.querySelector(".collection-item > .row > .col.s6.offset-s6 > strong");
        totalElem.textContent = "Total: $" + data.total_price;

        // Check if there are no items left in the cart AFTER removing the item
        const cartItems = document.querySelectorAll(".collection-item.avatar");
        if (cartItems.length === 0) {
          document.querySelector(".cart-container").style.display = "none";
          document.querySelector(".empty-cart-container").style.display = "flex";
        }

        // Display the notification
        showNotification(data.message, "success");
      } else {
        showNotification(data.message, "danger");
      }
    });
}
