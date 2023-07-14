$(document).ready(function () {
  // Hide alerts after 5 seconds
    $(".card-panel").delay(3000).slideUp(200, function() {
      $(this).remove(); 
  });

  // Clone the form once at the beginning
  var cloned_form = $(".reply-form").clone();

  $(".reply-button").on("click", function (event) {
    event.preventDefault();

    // hide all reply-buttons
    $(".reply-button").hide();

    var comment_id = $(this).attr("data-comment-id");

    // Clone the form from the originally cloned form
    var reply_form = cloned_form.clone();

    // Now remove any existing reply form
    $(".reply-form").remove();

    var reply_button = $(this);

    reply_form.find('[name="parent_comment"]').val(comment_id);

    // Add cancel button to the form
    var cancelButton =
      '<button type="button" class="cancel-button" style="color: white; background-color: red;">Cancelar</button>';
    if (!reply_form.html().includes(cancelButton)) {
      reply_form.append(cancelButton);
    }

    $(this).after(reply_form);
    reply_form.show();
    reply_form.find("textarea").focus(); // Focus on the textarea
  });

  $(document).on("click", ".cancel-button", function () {
    var reply_form = $(this).parents(".reply-form");
    var reply_button = reply_form.siblings(".reply-button");

    // Clear the form
    reply_form[0].reset();

    // Hide the form
    reply_form.remove(); // Remove the form entirely

    // Show all the reply buttons again
    $(".reply-button").show();
  });

  $(document).on("submit", ".reply-form", function (event) {
    event.preventDefault();

    var commentId = $(this).find('[name="parent_comment"]').val(); // get the comment ID from the hidden input
    var content = $(this).find('textarea[name="content"]').val();

    if (content.trim() == "") {
      // check if the reply is empty
      // Add the error message
      $(this).find(".error-message").remove(); // Remove any existing error messages
      $(this).append('<div class="error-message">Escribe aquí tu respuesta</div>');
      return;
    }

    var commentId = $(this).find('[name="parent_comment"]').val(); // get the comment ID from the hidden input

    var content = $(this).find('textarea[name="content"]').val();
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

    // save current scroll position
    var scrollPosition = $(window).scrollTop();

    // Include the parent comment ID and content in the data
    var formData = {
      content: content,
      parent_comment: commentId,
      csrfmiddlewaretoken: csrfmiddlewaretoken,
    };

    // Store the form in a variable
    var $form = $(this);

    // Store the reply placeholder
    var $replyPlaceholder = $form.siblings(".reply-placeholder");

    $.ajax({
      type: "POST",
      url: "/ajax/add_reply_to_comment/", // your endpoint to handle reply saving
      data: formData,
      success: function (response) {
        // add the new reply to the page
        var newReply =
          '<div class="comment reply">' +
          "<p>By " +
          response.author +
          "</p>" +
          "<p>on " +
          response.date +
          "</p>" +
          "<p>" +
          response.content +
          "</p>" +
          "</div>";

        // Clear and hide the form
        $form[0].reset();
        $form.remove();

        // Append the new reply to the stored reply placeholder
        $replyPlaceholder.append(newReply);

        $(".reply-button").show();

        // return to the saved scroll position
        $(window).scrollTop(scrollPosition);
      },
      error: function () {
        alert("Error while adding reply. Please try again.");
        // If there is an error, show the reply button again
        $(".reply-button").show();
      },
    });
  });

  $(".comment-form form").on("submit", function (event) {
    event.preventDefault();
    let form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: "json",
      success: function (data) {
        if (data.status == 1) {
          // Check if this is the first comment being posted
          let isFirstComment = $("#comment-section").children(".comment").length === 0;
          let commentHTML = `
            <div class="comment top-level">
              <p class="author">De ${data.author}</p>
              <p class="date">el ${data.date}</p>
              <p class="content">${data.content}</p>
              <!--<button class="reply-button" data-comment-id="${data.comment_id}">Responder</button>-->
              <div class="reply-placeholder"></div>
            </div>
          `;
          if (isFirstComment) {
              // Add the heading if it's the first comment
              let headingHTML = `<h2>Comentarios</h2>`;
              $("#comment-section").prepend(headingHTML);
          }
          $("#comment-section h2:first").after(commentHTML);
          $("#id_content").val("");
        } else {
          console.error("Error posting comment");
        }
      },
    });
  });

  $(".comment-form form textarea").on("focus", function () {
    var reply_form = $(".reply-form");
    var reply_button = reply_form.siblings(".reply-button");

    // Clear the form
    reply_form[0].reset();

    // Hide the form
    reply_form.remove(); // Remove the form entirely

    // Show all the reply buttons again
    $(".reply-button").show();
  });

  $.ajax({
      url: '/message_url/',  // Update this with the URL for the new Django view.
      type: 'get',  // This can be 'get' or 'post'
      dataType: 'json',
      success: function(data) {
          if (data.message) {
              Swal.fire({
                  icon: "success",
                  title: data.message,
                  showConfirmButton: false,
                  timer: 3000
              })
          }
      }
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

    if (!localStorage.getItem("popupShown") && !document.cookie.includes("subscribed=true") && isPopup && !localStorage.getItem("popupShown")) {
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
                title: 'Success!',
                text: data.message,
                icon: 'success',
                confirmButtonText: 'Ok'
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
