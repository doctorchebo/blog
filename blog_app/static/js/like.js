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
      var $countSpan = $button.next(".like-count"); // adjust this line
      var currentLikes = parseInt($countSpan.text(), 10) || 0; // if NaN, default to 0

      $.ajax({
        url: `/like_post/${postId}/`,
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
    });
  });