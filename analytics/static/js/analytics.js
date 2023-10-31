var startTime; // Variable to store the start time of the visit

$(document).ready(function () {
  startTracking();
});

function startTracking() {
  startTime = new Date(); // Record the start time when the page loads
}

function stopTracking() {
  var endTime = new Date();
  var durationInSeconds = (endTime - startTime) / 1000;
  var durationString = new Date(durationInSeconds * 1000).toISOString().substr(11, 8);

  var data = {
    url: window.location.pathname,
    duration: durationString,
    visit_date: new Date(),
  };

  // Add the CSRF token to the headers
  var headers = new Headers({
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken, // Use the csrfToken variable
  });

  // Create the request
  var request = new Request("/analytics/track_page_visit/", {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data),
  });

  // Send the request
  fetch(request)
    .then((response) => {
      if (response.ok) {
        console.log("Visited page:", data.url, "Duration:", durationString);
      } else {
        console.error("Error saving page visit data");
      }
    })
    .catch((error) => {
      console.error("Error sending the request:", error);
    });
}

window.addEventListener('beforeunload', function (event) {
  stopTracking();
});
