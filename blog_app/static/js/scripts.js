$(document).ready(function () {
  var initialPopupIntervalSeconds = 10; // 10 seconds
  var initialPopupIntervalMilliseconds = initialPopupIntervalSeconds * 1000;

  var popupIntervalMinutes = 5;
  var popupIntervalMilliseconds = popupIntervalMinutes * 60 * 1000;

  // Check if user is subscribed
  // userIsAuthenticated is global variable set in base.html
  if(userIsAuthenticated){
    $.ajax({
      url: "/blog/is_subscribed/",
      type: "get",
      dataType: "json",
      success: function (data) {
        if (!data.is_subscribed) {
          setupPopups();
        }
      },
      error: function () {
        setupPopups();
      },
    });
  }

  var validateEmail = function (email) {
    var regex = /^[a-zA-Z0-9._%+-]+@(gmail\.com|hotmail\.com|outlook\.com|yahoo\.com|protonmail\.com)$/;
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
        sessionStorage.setItem("popupLastShown", new Date().getTime().toString());
      };
    }

    // Check if popup has been shown this session
    if (!sessionStorage.getItem("popupShownThisSession")) {
      setTimeout(function () {
        if (!document.cookie.includes("subscribed=true")) {
          var popup = document.getElementById("subscribe-popup");
          popup.style.display = "block";
          sessionStorage.setItem("popupShownThisSession", "yes");
          sessionStorage.setItem("popupLastShown", new Date().getTime().toString());
        }
      }, initialPopupIntervalMilliseconds);
    }

    setInterval(function () {
      let lastShown = parseInt(sessionStorage.getItem("popupLastShown")) || 0;
      let currentTime = new Date().getTime();
      if (!document.cookie.includes("subscribed=true") && currentTime - lastShown > popupIntervalMilliseconds) {
        var popup = document.getElementById("subscribe-popup");
        popup.style.display = "block";
        sessionStorage.setItem("popupLastShown", new Date().getTime().toString());
      }
    }, popupIntervalMilliseconds);

    if(subscribeButton != null){
      subscribeButton.onclick = function () {
        var originalButtonContent = subscribeButton.innerHTML;
        var email = emailInput.value;
        if (email && validateEmail(email)) {
          subscribeButton.innerHTML =
            '<span class="spinner-border spinner-border-md" role="status" aria-hidden="true"></span>';
          subscribeButton.disabled = true;
          fetch("/blog/subscribe/", {
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
                subscribeButton.innerHTML = "Subscribe";
                subscribeButton.disabled = false;
                emailInput.value = "";
                document.cookie = "subscribed=true; max-age=31536000";
                popup.style.display = "none";
                Swal.fire({
                  title: "Éxito!",
                  text: data.message,
                  icon: "success",
                  confirmButtonText: "Ok",
                  customClass: {
                    confirmButton: "matrix-green-button",
                  },
                }).then((result) => {
                  // Redirect to /about page after user clicks Ok on the alert.
                  if (result.isConfirmed) {
                    window.location.href = "/blog/about/";
                  }
                });
              } else if (data.status === "ok" && !isPopup) {
                subscribeButton.innerHTML = "Subscribe";
                subscribeButton.disabled = false;
                emailInput.value = "";
                Swal.fire({
                  title: "Éxito!",
                  text: data.message,
                  icon: "success",
                  confirmButtonText: "Ok",
                  customClass: {
                    confirmButton: "matrix-green-button",
                  },
                }).then((result) => {
                  // Redirect to /about page after user clicks Ok on the alert.
                  if (result.isConfirmed) {
                    window.location.href = "/blog/about/";
                  }
                });
              }
            });
        } else {
          errorElement.textContent = "Por favor introduce un email válido.";
          subscribeButton.innerHTML = originalButtonContent;
        }
      };
    }
  };

  function setupPopups() {
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
  }

  // Hide alerts after 5 seconds
  $(".card-panel")
    .delay(3000)
    .slideUp(200, function () {
      $(this).remove();
    });
});
