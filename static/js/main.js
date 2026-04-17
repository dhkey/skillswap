function setupLandingSubjectTags() {
  var tagsContainer = document.getElementById("landingSubjectTags");
  if (!tagsContainer) {
    return;
  }

  tagsContainer.addEventListener("click", function (event) {
    var tag = event.target.closest(".subject-tag");
    if (!tag) {
      return;
    }

    tagsContainer.querySelectorAll(".subject-tag").forEach(function (el) {
      el.classList.remove("active");
    });
    tag.classList.add("active");
  });
}

function setupTutorSearchPage() {
  var grid = document.getElementById("tutorGrid");
  if (!grid) {
    return;
  }

  var cards = Array.from(grid.querySelectorAll(".tutor-card"));
  var resultCount = document.getElementById("resultCount");
  var emptyState = document.getElementById("emptyState");

  var searchInput = document.getElementById("searchInput");
  var locationInput = document.getElementById("locationInput");
  var availabilitySelect = document.getElementById("availabilitySelect");
  var searchButton = document.getElementById("searchButton");

  var priceMinInput = document.getElementById("priceMin");
  var priceMaxInput = document.getElementById("priceMax");

  var subjectPills = Array.from(document.querySelectorAll("#subjectPills .filter-pill"));
  var ratingChips = Array.from(document.querySelectorAll("#ratingChips .star-chip"));
  var formatButtons = Array.from(document.querySelectorAll(".toggle-btn[data-format]"));
  var sortButtons = Array.from(document.querySelectorAll(".sort-btn"));

  var toggleFilters = document.getElementById("toggleFilters");
  var filtersPanel = document.getElementById("filtersPanel");

  var loadMoreButton = document.getElementById("loadMoreButton");
  var loadHint = document.getElementById("loadHint");

  var state = {
    subject: "all",
    minRating: 4,
    formats: new Set(["online", "in-person"]),
    searchQuery: "",
    locationQuery: "",
    availability: "",
    minPrice: null,
    maxPrice: null,
    sortBy: "rating",
  };

  function normalize(text) {
    return (text || "")
      .toString()
      .toLowerCase()
      .trim();
  }

  function toNumber(value) {
    if (value === null || value === undefined || value === "") {
      return null;
    }

    var parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function cardMatches(card) {
    var cardSubject = normalize(card.dataset.subject);
    var rating = Number(card.dataset.rating || 0);
    var price = Number(card.dataset.price || 0);
    var formats = normalize(card.dataset.format).split(",").map(function (item) {
      return item.trim();
    });

    var textBlob = [
      card.dataset.name,
      card.dataset.subjectName,
      card.dataset.topics,
      card.dataset.availability,
    ]
      .join(" ")
      .toLowerCase();

    if (state.subject !== "all" && cardSubject !== state.subject) {
      return false;
    }

    if (rating < state.minRating) {
      return false;
    }

    if (state.minPrice !== null && price < state.minPrice) {
      return false;
    }

    if (state.maxPrice !== null && price > state.maxPrice) {
      return false;
    }

    if (state.formats.size > 0) {
      var hasFormatMatch = Array.from(state.formats).some(function (format) {
        return formats.includes(format);
      });
      if (!hasFormatMatch) {
        return false;
      }
    }

    if (state.searchQuery && !textBlob.includes(state.searchQuery)) {
      return false;
    }

    if (state.locationQuery) {
      var locationMatch = textBlob.includes(state.locationQuery) || state.locationQuery === "online";
      if (!locationMatch) {
        return false;
      }
    }

    if (state.availability) {
      var normalizedAvailability = normalize(card.dataset.availability);
      var expectedAvailability = state.availability.replace(/-/g, " ");
      if (!normalizedAvailability.includes(expectedAvailability)) {
        return false;
      }
    }

    return true;
  }

  function sortCards(sortBy) {
    var sorted = cards.slice();

    sorted.sort(function (a, b) {
      var ratingA = Number(a.dataset.rating || 0);
      var ratingB = Number(b.dataset.rating || 0);
      var reviewsA = Number(a.dataset.reviews || 0);
      var reviewsB = Number(b.dataset.reviews || 0);
      var priceA = Number(a.dataset.price || 0);
      var priceB = Number(b.dataset.price || 0);
      var indexA = Number(a.dataset.index || 0);
      var indexB = Number(b.dataset.index || 0);

      if (sortBy === "reviews") {
        return reviewsB - reviewsA;
      }
      if (sortBy === "price-low") {
        return priceA - priceB;
      }
      if (sortBy === "price-high") {
        return priceB - priceA;
      }
      if (sortBy === "newest") {
        return indexB - indexA;
      }
      if (ratingB === ratingA) {
        return reviewsB - reviewsA;
      }
      return ratingB - ratingA;
    });

    sorted.forEach(function (card) {
      grid.appendChild(card);
    });
  }

  function refreshResultCount(visibleCount) {
    if (resultCount) {
      resultCount.textContent = String(visibleCount);
    }
  }

  function showOrHideEmptyState(visibleCount) {
    if (!emptyState) {
      return;
    }

    emptyState.hidden = visibleCount !== 0;
  }

  function applyFilters() {
    var visibleCount = 0;

    cards.forEach(function (card) {
      var matches = cardMatches(card);
      card.style.display = matches ? "" : "none";
      if (matches) {
        visibleCount += 1;
      }
    });

    refreshResultCount(visibleCount);
    showOrHideEmptyState(visibleCount);
  }

  function runFilteringCycle() {
    sortCards(state.sortBy);
    applyFilters();
  }

  subjectPills.forEach(function (pill) {
    pill.addEventListener("click", function () {
      subjectPills.forEach(function (el) {
        el.classList.remove("active");
      });
      pill.classList.add("active");
      state.subject = normalize(pill.dataset.subject || "all");
      runFilteringCycle();
    });
  });

  ratingChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      ratingChips.forEach(function (el) {
        el.classList.remove("active");
      });
      chip.classList.add("active");
      state.minRating = Number(chip.dataset.rating || 0);
      runFilteringCycle();
    });
  });

  formatButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      button.classList.toggle("active");
      var formatKey = normalize(button.dataset.format);
      if (!formatKey) {
        return;
      }

      if (button.classList.contains("active")) {
        state.formats.add(formatKey);
      } else {
        state.formats.delete(formatKey);
      }

      runFilteringCycle();
    });
  });

  sortButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      sortButtons.forEach(function (el) {
        el.classList.remove("active");
      });
      button.classList.add("active");
      state.sortBy = normalize(button.dataset.sort || "rating");
      runFilteringCycle();
    });
  });

  function syncTextFilters() {
    state.searchQuery = normalize(searchInput ? searchInput.value : "");
    state.locationQuery = normalize(locationInput ? locationInput.value : "");
    state.availability = normalize(availabilitySelect ? availabilitySelect.value : "");
    state.minPrice = toNumber(priceMinInput ? priceMinInput.value : null);
    state.maxPrice = toNumber(priceMaxInput ? priceMaxInput.value : null);
    runFilteringCycle();
  }

  if (searchButton) {
    searchButton.addEventListener("click", syncTextFilters);
  }

  if (searchInput) {
    searchInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        syncTextFilters();
      }
    });
  }

  if (locationInput) {
    locationInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        syncTextFilters();
      }
    });
  }

  if (priceMinInput) {
    priceMinInput.addEventListener("input", syncTextFilters);
  }

  if (priceMaxInput) {
    priceMaxInput.addEventListener("input", syncTextFilters);
  }

  if (availabilitySelect) {
    availabilitySelect.addEventListener("change", syncTextFilters);
  }

  if (toggleFilters && filtersPanel) {
    toggleFilters.addEventListener("click", function () {
      filtersPanel.classList.toggle("collapsed");
      var isCollapsed = filtersPanel.classList.contains("collapsed");
      toggleFilters.textContent = isCollapsed
        ? "Show advanced filters"
        : "Hide advanced filters";
    });
  }

  if (loadMoreButton) {
    loadMoreButton.addEventListener("click", function () {
      loadMoreButton.disabled = true;
      loadMoreButton.textContent = "No more tutors";
      if (loadHint) {
        loadHint.textContent = "You have reached the end of the current results.";
      }
    });
  }

  runFilteringCycle();
}

document.addEventListener("DOMContentLoaded", function () {
  setupLandingSubjectTags();
  setupTutorSearchPage();
});
