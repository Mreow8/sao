$(document).ready(function () {
  // --- Accordion Menu Logic ---
  var $navButtons = $(".side-nav > ul > li > a");

  $navButtons.on("click", function (e) {
    var $this = $(this); // The button that was clicked
    var $submenu = $this.next("ul"); // The submenu associated with it
    var href = ($this.attr("href") || "").trim();

    // If the clicked menu has no submenu, allow normal navigation
    if ($submenu.length === 0) {
      if (href === "#" || href === "") {
        e.preventDefault();
      }
      // Otherwise, let the link work
      return;
    }

    // It *does* have a submenu, so prevent default link behavior
    e.preventDefault();

    // --- THIS IS THE LOGIC THAT DOES WHAT YOU WANT ---

    // Check if the clicked menu is already active
    if ($this.hasClass("active")) {
      // BEHAVIOR 2: It is active, so CLOSE it (this allows toggling)
      $submenu.removeClass("active").slideUp();
      $this.removeClass("active");
      $this.find(".fas").removeClass("rotate");
    } else {
      // BEHAVIOR 1: It is not active, so CLOSE all OTHERS and OPEN this one

      // 1. Find all *other* open submenus
      var $openSubmenus = $(".side-nav ul li ul.active");
      // 2. Close them
      $openSubmenus.removeClass("active").slideUp();
      // 3. Find their buttons and deactivate them
      var $activeButtons = $(".side-nav > ul > li > a.active").not($this);
      $activeButtons.removeClass("active");
      // 4. Reset their carets
      $activeButtons.find(".fas").removeClass("rotate");

      // 5. Now, open the *newly clicked* submenu
      $submenu.addClass("active").slideDown();
      $this.addClass("active");
      // 6. Rotate its caret
      $this.find(".fas").addClass("rotate");
    }
  });
});

// NOTE: I have removed the mobile toggle logic from this file.
// You already have it in main.html, so it's not needed here.
