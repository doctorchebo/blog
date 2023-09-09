function showNotification(message, type) {
    const notificationContainer = document.createElement("div");
    notificationContainer.className = "container fixed-notification-container"; 

    const notification = document.createElement("div");
    if (type === "success") {
      notification.className = "card-panel white-text #1b5e20 green darken-4 center";
    } else {
      notification.className = "card-panel white-text red darken-4 center";
    }

    notification.innerText = message;
    notificationContainer.appendChild(notification);
    document.querySelector("body").prepend(notificationContainer); 

    // Auto remove the notification after 3 seconds
    setTimeout(() => {
      notificationContainer.remove();
    }, 3000);
  }