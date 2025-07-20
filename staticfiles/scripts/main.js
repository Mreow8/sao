let currentMenu = null;

// Function to close all menus
function closeAllMenus() {
  const allSubmenus = [
    ".scholar-show",
    ".jobplace-show",
    ".student_disc-show",
    ".guide-show",
    ".alumni-show",
    ".community-show",
    ".student_org-show",
    ".medical-show",
    ".studentlife",
  ];
  const allIndicators = [
    ".first",
    ".second",
    ".third",
    ".fourth",
    ".fifth",
    ".sixth",
    ".seventh",
    ".eight",
    ".ninth",
  ];

  allSubmenus.forEach((cls) =>
    $(cls).removeClass("show show2 show3 show4 show5 show6 show7 show8 show9")
  );
  allIndicators.forEach((cls) => $(cls).removeClass("rotate"));
  currentMenu = null;
}

// General function to toggle a menu
function toggleMenu(
  btnSelector,
  submenuSelector,
  rotateSelector,
  menuKey,
  showClass
) {
  $(btnSelector).on("click", function (e) {
    // Prevent link inside button (if any) from triggering page reload
    e.preventDefault();

    // If we're clicking the same menu again, do nothing (keep it open)
    if (currentMenu === menuKey) {
      return;
    }

    // Otherwise, close everything and open the new menu
    closeAllMenus();
    $(submenuSelector).addClass(showClass);
    $(rotateSelector).addClass("rotate");
    currentMenu = menuKey;
  });
}

// Set up all the menu buttons
toggleMenu(".scholar-btn", ".scholar-show", ".second", "scholar", "show2");
toggleMenu(".jobplace-btn", ".jobplace-show", ".third", "jobplace", "show3");
toggleMenu(".studentlife-btn", ".studentlife", ".first", "studentlife", "show");
toggleMenu(
  ".student_disc-btn",
  ".student_disc-show",
  ".fourth",
  "student_disc",
  "show4"
);
toggleMenu(".guide-btn", ".guide-show", ".fifth", "guide", "show5");
toggleMenu(".alumni-btn", ".alumni-show", ".sixth", "alumni", "show6");
toggleMenu(
  ".community-btn",
  ".community-show",
  ".seventh",
  "community",
  "show7"
);
toggleMenu(
  ".student_org-btn",
  ".student_org-show",
  ".eight",
  "student_org",
  "show8"
);
toggleMenu(".medical-btn", ".medical-show", ".ninth", "medical", "show9");
