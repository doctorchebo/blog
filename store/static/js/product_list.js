function decreaseQuantity(productId) {
  let quantitySpan = document.getElementById(`quantity-${productId}`);
  let currentValue = parseInt(quantitySpan.innerText, 10);
  if (currentValue > 0) {
    // changed from 1 to 0 to allow decrease to 0
    quantitySpan.innerText = currentValue - 1;
  }
}

function increaseQuantity(productId) {
  let quantitySpan = document.getElementById(`quantity-${productId}`);
  let currentValue = parseInt(quantitySpan.innerText, 10);
  quantitySpan.innerText = currentValue + 1;
}

function addToCart(productId) {
  let quantityElement = document.getElementById(`quantity-${productId}`);
  let quantity = quantityElement ? quantityElement.innerText : "1";
  // Send an AJAX POST request
  fetch(addToCartUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: quantity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Display the notification
        showNotification(data.message, "success");
        document.getElementById("cart-icon-container").classList.remove("hidden");

        // Update cart count
        document.getElementById("cart-counter").textContent = data.cart_count;
      } else {
        showNotification(data.message, "danger");
      }
    });
}
