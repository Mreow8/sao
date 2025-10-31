// --- orgfinal.js ---

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. "Add Element" Script for Edit Mode ---
  const addElementBtn = document.getElementById("add-element-btn");
  if (addElementBtn) {
    addElementBtn.addEventListener("click", function () {
      const container = document.getElementById("key-elements-container");
      const div = document.createElement("div");
      div.classList.add("key-element");
      div.innerHTML = `
        <input type="text" name="key_elements[]" placeholder="Enter new element meaning..." class="key-input" />
      `;
      container.appendChild(div);
    });
  }

  // --- 2. Adviser Modal Script ---
  const modalOverlay = document.getElementById("adviser-modal-overlay");
  const modalIframe = document.getElementById("adviser-form-iframe");
  const openBtn = document.getElementById("register-adviser-btn");
  const closeBtn = document.getElementById("modal-close-button");

  // Function to open the modal
  function openAdviserModal(url) {
    if (modalOverlay && modalIframe) {
      modalIframe.src = url;
      modalOverlay.classList.add("show");
    }
  }

  // Function to close the modal
  function closeAdviserModal() {
    if (modalOverlay && modalIframe) {
      modalOverlay.classList.remove("show");

      // Clear src AFTER the animation finishes (300ms) to prevent white flash
      setTimeout(() => {
        modalIframe.src = "";
      }, 300);

      // Optional: Refresh parent page to show new data
      // You can also use a confirm dialog
      // if (confirm("Reload page to see the new adviser?")) {
      //   window.location.reload();
      // }
    }
  }

  // --- Event Listeners ---

  // Listen for click on the "Register Adviser" button
  if (openBtn) {
    openBtn.addEventListener("click", function () {
      const url = this.getAttribute("data-url");
      openAdviserModal(url);
    });
  }

  // Listen for click on the modal's "X" close button
  if (closeBtn) {
    closeBtn.addEventListener("click", closeAdviserModal);
  }

  // Listen for click on the dark overlay to close
  if (modalOverlay) {
    modalOverlay.addEventListener("click", function (event) {
      // Only close if the click is on the overlay itself, not the modal content
      if (event.target === this) {
        closeAdviserModal();
      }
    });
  }

  // Make close function globally available IFRAME communication
  // This allows the iframe form to call `window.parent.closeModalFromIframe()` on success
  window.closeModalFromIframe = function () {
    closeAdviserModal();
    // You might want to auto-reload here
    window.location.reload();
  };
});
