document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const searchButton = document.getElementById("searchButton");

  searchButton.addEventListener("click", function () {
    const searchTerm = searchInput.value.trim();
    const selectedCategory = categoryFilter.value;

    // Retrieve the post list URL from the data attribute
    const postListUrl = searchButton.getAttribute("data-post-list-url");

    // Construct the search URL based on user input
    let searchUrl = postListUrl + "?";
    if (searchTerm !== "") {
      searchUrl += `q=${encodeURIComponent(searchTerm)}&`;
    }
    if (selectedCategory !== "") {
      searchUrl += `category=${selectedCategory}&`;
    }

    // Redirect to the search URL
    window.location.href = searchUrl;
  });
});
