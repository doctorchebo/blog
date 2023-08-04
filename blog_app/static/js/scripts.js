$(document).ready(function () {
  // Hide alerts after 5 seconds
  $(".card-panel")
    .delay(3000)
    .slideUp(200, function () {
      $(this).remove();
    });

  $.ajax({
    url: "/message_url/", // Update this with the URL for the new Django view.
    type: "get", // This can be 'get' or 'post'
    dataType: "json",
    success: function (data) {
      if (data.message) {
        Swal.fire({
          icon: "success",
          title: data.message,
          showConfirmButton: false,
          timer: 3000,
        });
      }
    },
  });
});
window.onload = function () {
  // Email validation function
  var validateEmail = function (email) {
    var regex = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/;
    return regex.test(email);
  };

  var setupSubscriptionForm = function (popupId, emailId, errorId, buttonId, closeId, isPopup) {
    var popup = document.getElementById(popupId);
    var subscribeButton = document.getElementById(buttonId);
    var emailInput = document.getElementById(emailId);
    var errorElement = document.getElementById(errorId);

    if (isPopup) {
      var closeButton = document.getElementById(closeId);
      closeButton.onclick = function () {
        popup.style.display = "none";
      };
    }

    if (
      !localStorage.getItem("popupShown") &&
      !document.cookie.includes("subscribed=true") &&
      isPopup &&
      !localStorage.getItem("popupShown")
    ) {
      setTimeout(function () {
        popup.style.display = "block";
      }, 5000);
      localStorage.setItem("popupShown", "yes");
    }

    subscribeButton.onclick = function () {
      var email = emailInput.value;
      if (email && validateEmail(email)) {
        // validate email before sending to server
        fetch("/subscribe/", {
          method: "POST",
          body: JSON.stringify({ email: email }),
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
        })
          .then(function (response) {
            return response.json();
          })
          .then(function (data) {
            errorElement.textContent = data.message;
            if (data.status === "ok" && isPopup) {
              document.cookie = "subscribed=true; max-age=31536000";
              popup.style.display = "none";
              Swal.fire({
                title: "Éxito!",
                text: data.message,
                icon: "success",
                confirmButtonText: "Ok",
              });
            } else if (data.status === "ok" && !isPopup) {
              // This is the new part for the subscribe page.
              Swal.fire({
                title: "Éxito!",
                text: data.message,
                icon: "success",
                confirmButtonText: "Ok",
              }).then((result) => {
                // Redirect to /about page after user clicks Ok on the alert.
                if (result.isConfirmed) {
                  window.location.href = "/about/";
                }
              });
            }
          });
      } else {
        errorElement.textContent = "Por favor introduce un email válido.";
      }
    };
  };

  setupSubscriptionForm(
    "subscribe-popup",
    "subscriber-email-popup",
    "subscribe-error-popup",
    "subscribe-button-popup",
    "close-popup",
    true
  );
  setupSubscriptionForm(
    "subscribe-page",
    "subscriber-email-page",
    "subscribe-error-page",
    "subscribe-button-page",
    "",
    false
  );

  var closeButton = document.getElementById("close-popup");
  closeButton.onclick = function () {
    var popup = document.getElementById("subscribe-popup");
    popup.style.display = "none";
  };
};
