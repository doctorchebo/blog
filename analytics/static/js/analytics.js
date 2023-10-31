var startTime; // Variable to store the start time of the visit

$(document).ready(function () {
  startTracking();
});

function startTracking() {
  startTime = new Date(); // Record the start time when the page loads
}

function stopTracking() {
  var endTime = new Date(); // Record the end time when the user navigates away

  var durationInSeconds = (endTime - startTime) / 1000; // Calculate the duration in seconds

  // Format the duration as a string in the 'hh:mm:ss' format
  var durationString = new Date(durationInSeconds * 1000).toISOString().substr(11, 8);

  // Send data to the server (you can use AJAX to send this data)
  var data = {
    url: window.location.pathname, // Current page URL
    duration: durationString, // Send the duration as a string
    visit_date: new Date(),
  };

  // Send the data to the server using an AJAX request (you may use a library like jQuery or Fetch API)
  // Replace 'your_server_endpoint' with your server-side endpoint to save the data
  // Example using Fetch API:
  fetch("/analytics/track_page_visit/", {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
    },
  });
}


window.addEventListener('beforeunload', function (event) {
  stopTracking();
});
