$(document).ready(function () {
  // --- Accordion Menu Logic ---
  var $navButtons = $(".side-nav > ul > li > a");

  $navButtons.on("click", function (e) {
    var $this = $(this); // The button that was clicked
    var $submenu = $this.next("ul"); // The submenu associated with it
    var href = ($this.attr("href") || "").trim();

    // If the clicked menu has no submenu, allow normal navigation
    // (unless href is '#' which we should prevent)
    if ($submenu.length === 0) {
      if (href === "#" || href === "") {
        e.preventDefault();
      }
      // Otherwise, let the link work (e.g., href="/some-page/")
      return;
    }

    // If it *does* have a submenu, prevent default navigation
    e.preventDefault();

    // If the clicked menu is *already* active, do nothing.
    // This is the "dont fold until we click another" logic.
    if ($this.hasClass("active")) {
      return;
    }

    // 1. Find all *other* submenus that are currently open
    var $openSubmenus = $(".side-nav ul li ul.active");

    // 2. Close them
    $openSubmenus.removeClass("active").slideUp();

    // 3. Find their corresponding buttons and deactivate them
    var $activeButtons = $(".side-nav > ul > li > a.active").not($this);
    $activeButtons.removeClass("active");

    // 4. Reset their carets
    $activeButtons.find(".fas").removeClass("rotate");

    // 5. Now, open the *newly clicked* submenu and activate its button
    $submenu.addClass("active").slideDown();
    $this.addClass("active");

    // 6. Rotate its caret
    $this.find(".fas").addClass("rotate");
  });
});

// --- Mobile Sidebar Toggle Logic ---
// (This code is correct, leaving it as-is)
(function () {
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const leftSide = document.querySelector(".left-side");

  if (sidebarToggle && leftSide) {
    sidebarToggle.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent click from bubbling to document
      leftSide.classList.toggle("active");
    });

    // Hide sidebar when clicking outside on small screens
    document.addEventListener("click", function (e) {
      if (
        window.innerWidth <= 900 &&
        leftSide.classList.contains("active") &&
        !leftSide.contains(e.target) &&
        e.target !== sidebarToggle
      ) {
        leftSide.classList.remove("active");
      }
    });

    // Remove .active on resize to large screens
    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) {
        leftSide.classList.remove("active");
        leftSide.style.transform = "";
      }
    });
  }
})();
