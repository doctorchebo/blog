// like button
$(document).ready(function () {
  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
  }
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", $("input[name=csrfmiddlewaretoken]").val());
      }
    },
  });

  $("body").on("click", ".like-button", function () {
    var $button = $(this);
    var postId = $button.data("post-id");
    var $countSpan = $button.next(".like-count");
    var currentLikes = parseInt($countSpan.text(), 10) || 0;
    // Check if the user is authenticated
    if (userIsAuthenticated) {
      // User is authenticated, perform the like action
      $.ajax({
        url: `/blog/like_post/${postId}/`,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ post_id: postId }),
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        success: function (data) {
          if (data.liked) {
            $button.addClass("liked");
            $countSpan.text(currentLikes + 1); // Increment the like count
          } else {
            $button.removeClass("liked");
            $countSpan.text(currentLikes - 1); // Decrement the like count
          }
        },
      });
    } else {
      console.log("show popup");
      // User is not authenticated, show the popup
      showLikePopup();
    }
  });
  // Function to show the like popup
  function showLikePopup() {
    // Find the like popup element by its class and make it visible
    var likePopup = document.getElementById("like-popup");
    likePopup.style.display = "block";
    var closeButton = document.getElementById("close-like-popup");
    closeButton.onclick = function () {
      console.log("clicked");
      likePopup.style.display = "none";
    };
  }
});
