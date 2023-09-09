document.addEventListener("DOMContentLoaded", function () {
  // Get all content_type selects
  let contentTypes = document.querySelectorAll('select[name$="content_type"]');

  // Loop through all content_type selects and attach event listener
  contentTypes.forEach((contentType) => {
    contentType.addEventListener("change", function () {
      // For each content_type, get the corresponding object_id select in the same row
      let objectId = this.closest("tr").querySelector('select[name$="object_id"]');

      console.log("triggered");
      let selectedValue = this.value;

      // Fetch the data
      fetch(`/store/get_content_objects/${selectedValue}/`)
        .then((response) => response.json())
        .then((data) => {
          // Clear current options
          while (objectId.firstChild) {
            objectId.removeChild(objectId.firstChild);
          }

          // Add an empty option as placeholder
          let placeholderOption = document.createElement("option");
          placeholderOption.value = "";
          placeholderOption.textContent = "----";
          objectId.appendChild(placeholderOption);

          // Populate new options
          for (let key in data) {
            let option = document.createElement("option");
            option.value = key; // The key is the ID, which should be used as the value
            option.textContent = data[key]; // The value is the name, which should be used as the display text
            objectId.appendChild(option);
          }
        });
    });
  });
});
