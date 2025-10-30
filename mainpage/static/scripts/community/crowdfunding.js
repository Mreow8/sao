// --- FIX --- All code is now wrapped in one DOMContentLoaded listener
document.addEventListener("DOMContentLoaded", function () {
  // --- NEW: Helper function to get CSRF token (from programs.js) ---
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // --- NEW: Configure the toast notification (from programs.js) ---
  const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener("mouseenter", Swal.stopTimer);
      toast.addEventListener("mouseleave", Swal.resumeTimer);
    },
  });

  // --- Logic for 3-dot menu ---
  const projectList = document.querySelector(".project-list");
  if (projectList) {
    projectList.addEventListener("click", function (e) {
      if (e.target.classList.contains("menu-btn")) {
        // Hide all other menus
        document.querySelectorAll(".menu").forEach((menu) => {
          if (menu !== e.target.nextElementSibling) {
            menu.classList.add("hidden");
          }
        });
        // Show the menu next to the clicked button
        const menu = e.target.nextElementSibling;
        if (menu) menu.classList.toggle("hidden");
        e.stopPropagation();
      }
    });
  }
  // Hide menus when clicking outside
  document.body.addEventListener("click", function () {
    document
      .querySelectorAll(".menu")
      .forEach((menu) => menu.classList.add("hidden"));
  });

  // --- Logic for Delete Confirmation ---
  document.querySelectorAll(".delete-project-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      Swal.fire({
        title: "Are you sure?",
        text: "This action cannot be undone.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });

  // --- Logic for "Add Event" Form (Unchanged) ---
  const collapsedBox = document.getElementById("collapsedBox");
  const expandedBox = document.getElementById("expandedBox");
  const postText = document.getElementById("postText");
  const submitBtn = document.getElementById("submitBtn");
  const postForm = document.getElementById("expandedBox");
  const popup = document.getElementById("popup");
  const imageUpload = document.getElementById("imageUpload");
  const preview = document.getElementById("preview");

  if (collapsedBox) {
    // ... (rest of your add event form logic is fine) ...
    collapsedBox.addEventListener("click", () => {
      collapsedBox.style.display = "none";
      expandedBox.style.display = "flex";
      postText.focus();
    });
  }
  if (postText) {
    postText.addEventListener("input", () => {
      submitBtn.disabled = postText.value.trim() === "";
    });
  }
  if (imageUpload) {
    // ... (rest of your image preview logic is fine) ...
    imageUpload.addEventListener("change", () => {
      preview.innerHTML = "";
      const files = Array.from(imageUpload.files);
      files.forEach((file, index) => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("preview-item");
        let media;
        if (file.type.startsWith("image/")) {
          media = document.createElement("img");
          media.src = URL.createObjectURL(file);
        } else if (file.type.startsWith("video/")) {
          media = document.createElement("video");
          media.src = URL.createObjectURL(file);
          media.controls = true;
        }
        wrapper.appendChild(media);

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "×";
        removeBtn.classList.add("remove-btn");
        removeBtn.addEventListener("click", () => {
          files.splice(index, 1);
          updateFileList(files);
          wrapper.remove();
        });
        wrapper.appendChild(removeBtn);
        preview.appendChild(wrapper);
      });
    });
  }
  function updateFileList(files) {
    const dt = new DataTransfer();
    files.forEach((f) => dt.items.add(f));
    imageUpload.files = dt.files;
  }
  if (postForm) {
    // ... (rest of your AJAX form submission logic is fine) ...
    postForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(postForm);
      const url = postForm.action;
      fetch(url, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            // This part is fine, but you could change it to reload()
            // to show the new post on top if pagination isn't active
            location.reload();
          }
        })
        .catch((err) => {
          if (popup) {
            popup.style.display = "block";
            popup.textContent = "Error: " + err.message;
            setTimeout(() => (popup.style.display = "none"), 3000);
          }
        });
    });
  }

  // --- NEW: Edit Modal Logic (from programs.js) ---
  const editModal = document.getElementById("editModal");
  const modalContent = document.getElementById("modalContent");

  if (projectList) {
    // Event listener to open the modal
    projectList.addEventListener("click", function (event) {
      const editButton = event.target.closest(".edit-project-btn");
      if (editButton) {
        event.preventDefault();
        const url = editButton.dataset.url;

        fetch(url, {
          headers: { "X-Requested-with": "XMLHttpRequest" },
        })
          .then((res) => res.json())
          .then((data) => {
            // Check for both keys, just in case
            const html = data.form_html || data.html_form;
            if (html) {
              modalContent.innerHTML = html;
              editModal.classList.remove("hidden");
              editModal.classList.add("flex");
            } else {
              console.error("Failed to load form HTML from response.");
            }
          })
          .catch((err) => console.error("Error fetching edit form:", err));
      }
    });
  }

  // Event listener to handle the form submission *inside* the modal
  if (modalContent) {
    modalContent.addEventListener("submit", function (e) {
      // Check if the submitted form is the edit form
      if (e.target.id === "editProgramForm" || e.target.closest("form")) {
        e.preventDefault();
        const form = e.target.closest("form");
        const formData = new FormData(form);

        fetch(form.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.success) {
              // --- This is the key change ---
              // 1. Find the card on the page
              const projectCard = document.getElementById(
                `program-${data.project.id}`
              );

              if (projectCard) {
                // 2. Update its content directly
                projectCard.querySelector(".text-lg").textContent =
                  data.project.title;
                projectCard.querySelector(".text-sm").textContent =
                  data.project.description;
                // You can update other fields here if needed
              }

              // 3. Close the modal
              closeModal();

              // 4. Show success toast
              Toast.fire({
                icon: "success",
                title: "Saved successfully!",
              });
            } else if (data.form_html) {
              // Re-render the form with validation errors
              modalContent.innerHTML = data.form_html;
            } else {
              console.error("Form errors:", data.errors);
              Swal.fire(
                "Error!",
                "Please correct the errors and try again.",
                "error"
              );
            }
          })
          .catch((err) => {
            console.error("Error submitting edit form:", err);
            Swal.fire("Error!", "An unexpected error occurred.", "error");
          });
      }
    });
  }

  // Function to close the modal
  function closeModal() {
    if (editModal) {
      editModal.classList.add("hidden");
      editModal.classList.remove("flex");
    }
    if (modalContent) {
      modalContent.innerHTML = "";
    }
  }

  // Event listener to close the modal on background click or close button
  if (editModal) {
    editModal.addEventListener("click", function (e) {
      // Check for close button (if one is rendered in your form_html)
      if (
        e.target.classList.contains("btn-close-modal") ||
        e.target.id === "editModal"
      ) {
        closeModal();
      }
    });
  }

  // Also listen for close button clicks *inside* the modal content
  if (modalContent) {
    modalContent.addEventListener("click", function (e) {
      if (e.target.classList.contains("btn-close-modal")) {
        closeModal();
      }
    });
  }
}); // --- End of DOMContentLoaded listener
