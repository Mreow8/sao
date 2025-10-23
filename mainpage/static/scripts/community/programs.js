document.addEventListener("DOMContentLoaded", function () {
  // Helper function to get CSRF token
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

  // Configure the toast notification
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

  // --- Logic for the "Add Events" form ---
  const postForm = document.getElementById("expandedBox");
  if (postForm) {
    const collapsedBox = document.getElementById("collapsedBox");
    const expandedBox = document.getElementById("expandedBox");
    const postText = document.getElementById("postText");
    const submitBtn = document.getElementById("submitBtn");
    const imageUpload = document.getElementById("imageUpload");
    const preview = document.getElementById("preview");
    const addProgramUrl = postForm.dataset.addUrl;

    collapsedBox.addEventListener("click", () => {
      collapsedBox.style.display = "none";
      expandedBox.style.display = "flex";
      postText.focus();
    });

    postText.addEventListener("input", () => {
      submitBtn.disabled = postText.value.trim() === "";
    });

    let currentFiles = [];
    imageUpload.addEventListener("change", () => {
      currentFiles = Array.from(imageUpload.files);
      updatePreview(currentFiles);
    });

    function updateFileList(files) {
      const dt = new DataTransfer();
      files.forEach((f) => dt.items.add(f));
      imageUpload.files = dt.files;
    }

    function updatePreview(files) {
      preview.innerHTML = "";
      files.forEach((file, index) => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("preview-item");
        let media;
        if (file.type.startsWith("image/")) {
          media = document.createElement("img");
        } else if (file.type.startsWith("video/")) {
          media = document.createElement("video");
          media.controls = true;
        }
        media.src = URL.createObjectURL(file);
        wrapper.appendChild(media);

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "×";
        removeBtn.classList.add("remove-btn");
        removeBtn.addEventListener("click", () => {
          files.splice(index, 1);
          updateFileList(files);
          updatePreview(files);
        });
        wrapper.appendChild(removeBtn);
        preview.appendChild(wrapper);
      });
    }

    postForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(postForm);
      fetch(addProgramUrl, {
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
            location.reload();
          }
        })
        .catch((err) => {
          console.error("Error submitting form:", err);
          alert("An error occurred. Please try again.");
        });
    });
  }

  // --- Logic for Edit/Delete Menu (Toggling visibility) ---
  const programList = document.querySelector(".program-list");
  if (programList) {
    programList.addEventListener("click", function (e) {
      if (e.target.classList.contains("menu-btn")) {
        document.querySelectorAll(".menu").forEach((menu) => {
          if (menu !== e.target.nextElementSibling) {
            menu.classList.add("hidden");
          }
        });
        e.target.nextElementSibling.classList.toggle("hidden");
        e.stopPropagation();
      }
    });
  }

  document.body.addEventListener("click", function () {
    document
      .querySelectorAll(".menu")
      .forEach((menu) => menu.classList.add("hidden"));
  });

  // --- Logic for Delete Confirmation ---
  document.querySelectorAll(".delete-program-form").forEach(function (form) {
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

  // --- Logic for Edit Modal ---
  const editModal = document.getElementById("editModal");
  const modalContent = document.getElementById("modalContent");

  if (programList) {
    programList.addEventListener("click", function (e) {
      if (e.target.classList.contains("edit-program-btn")) {
        const url = e.target.dataset.url;
        fetch(url, {
          headers: { "X-Requested-with": "XMLHttpRequest" },
        })
          .then((res) => res.json())
          .then((data) => {
            modalContent.innerHTML = data.html_form;
            editModal.classList.remove("hidden");
            editModal.classList.add("flex");
          });
      }
    });
  }

  modalContent.addEventListener("submit", function (e) {
    if (e.target.id === "editProgramForm") {
      e.preventDefault();
      const form = e.target;
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
            const programCard = document.getElementById(
              `program-${data.program.id}`
            );
            programCard.querySelector(".program-title").textContent =
              data.program.title;
            programCard.querySelector(".program-caption").textContent =
              data.program.caption;
            programCard.querySelector(".program-description").textContent =
              data.program.description;

            closeModal();

            Toast.fire({
              icon: "success",
              title: "Saved successfully!",
            });
          } else {
            console.error("Form errors:", data.errors);
            alert("Please correct the errors and try again.");
          }
        });
    }
  });

  function closeModal() {
    editModal.classList.add("hidden");
    editModal.classList.remove("flex");
    modalContent.innerHTML = "";
  }

  editModal.addEventListener("click", function (e) {
    if (
      e.target.classList.contains("btn-close-modal") ||
      e.target.id === "editModal"
    ) {
      closeModal();
    }
  });
});
