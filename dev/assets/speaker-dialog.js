/**
 * Speaker Dialog Management
 * Handles opening and closing of speaker information dialogs
 */
(function() {
  'use strict';

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Get all info buttons
    const infoButtons = document.querySelectorAll('.speaker-info-btn');

    infoButtons.forEach(button => {
      button.addEventListener('click', handleInfoClick);
    });

    // Get all close buttons
    const closeButtons = document.querySelectorAll('.speaker-dialog-close');
    closeButtons.forEach(button => {
      button.addEventListener('click', handleCloseClick);
    });

    // Get all dialogs
    const dialogs = document.querySelectorAll('.speaker-dialog');
    dialogs.forEach(dialog => {
      // Close on backdrop click
      dialog.addEventListener('click', handleBackdropClick);
    });
  }

  function handleInfoClick(event) {
    const speakerId = event.currentTarget.getAttribute('data-speaker');
    const dialog = document.getElementById('dialog-' + speakerId);

    if (dialog) {
      dialog.showModal();
      // Focus is automatically managed by the dialog element
    }
  }

  function handleCloseClick(event) {
    const dialog = event.currentTarget.closest('dialog');
    if (dialog) {
      dialog.close();
    }
  }

  function handleBackdropClick(event) {
    // Only close if clicking the backdrop (::backdrop), not content
    const dialog = event.currentTarget;
    const rect = dialog.getBoundingClientRect();

    if (
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom
    ) {
      dialog.close();
    }
  }
})();
