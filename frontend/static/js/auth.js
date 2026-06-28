(function () {
  const tabs = document.querySelectorAll('.auth-tab');
  const loginPanel = document.getElementById('auth-login-panel');
  const registerPanel = document.getElementById('auth-register-panel');

  function setActivePanel(panel) {
    tabs.forEach((tab) => {
      tab.classList.toggle('is-active', tab.dataset.panel === panel);
    });

    if (window.matchMedia('(max-width: 899px)').matches) {
      loginPanel?.classList.toggle('is-hidden-mobile', panel !== 'login');
      registerPanel?.classList.toggle('is-hidden-mobile', panel !== 'register');
    } else {
      loginPanel?.classList.remove('is-hidden-mobile');
      registerPanel?.classList.remove('is-hidden-mobile');
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => setActivePanel(tab.dataset.panel));
  });

  window.addEventListener('resize', () => {
    const active = document.querySelector('.auth-tab.is-active');
    if (active) setActivePanel(active.dataset.panel);
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get('register_open') === '1' || params.get('register_error')) {
    setActivePanel('register');
  } else {
    setActivePanel('login');
  }

  document.querySelectorAll('[data-toggle-password]').forEach((button) => {
    const inputId = button.getAttribute('data-toggle-password');
    const input = document.getElementById(inputId);
    if (!input) return;

    button.addEventListener('click', () => {
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      button.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
      button.classList.toggle('is-visible', isPassword);
    });
  });

  const profilePictureInput = document.getElementById('profile-picture-input');
  const profilePreview = document.getElementById('profile-preview');
  const profilePreviewPlaceholder = document.getElementById('profile-preview-placeholder');
  const chooseFileBtn = document.getElementById('choose-file-btn');
  const cameraPanel = document.getElementById('camera-panel');
  const cameraVideo = document.getElementById('camera-video');
  let cameraStream = null;

  function showPreviewFromFile(file) {
    if (!file || !profilePreview) return;
    const reader = new FileReader();
    reader.onload = () => {
      profilePreview.src = reader.result;
      profilePreview.hidden = false;
      profilePreviewPlaceholder?.setAttribute('hidden', '');
    };
    reader.readAsDataURL(file);
  }

  function setProfilePictureFile(file) {
    if (!profilePictureInput) return;
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    profilePictureInput.files = dataTransfer.files;
    showPreviewFromFile(file);
  }

  chooseFileBtn?.addEventListener('click', () => profilePictureInput?.click());

  profilePictureInput?.addEventListener('change', () => {
    const file = profilePictureInput.files?.[0];
    if (file) showPreviewFromFile(file);
  });

  async function startCamera() {
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });
      if (cameraVideo) {
        cameraVideo.srcObject = cameraStream;
      }
      cameraPanel?.removeAttribute('hidden');
    } catch {
      alert('Camera access is not available. You can still upload a photo file.');
    }
  }

  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
      cameraStream = null;
    }
    if (cameraVideo) cameraVideo.srcObject = null;
    cameraPanel?.setAttribute('hidden', '');
  }

  async function captureCameraPhoto() {
    if (!cameraStream || !cameraVideo) return;
    const canvas = document.createElement('canvas');
    const videoWidth = cameraVideo.videoWidth || 720;
    const videoHeight = cameraVideo.videoHeight || 720;
    canvas.width = videoWidth;
    canvas.height = videoHeight;
    canvas.getContext('2d').drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `camera-photo-${Date.now()}.png`, { type: 'image/png' });
      setProfilePictureFile(file);
      stopCamera();
    }, 'image/png', 0.95);
  }

  function clearProfilePhoto() {
    if (profilePictureInput) profilePictureInput.value = '';
    if (profilePreview) {
      profilePreview.src = '';
      profilePreview.hidden = true;
    }
    profilePreviewPlaceholder?.removeAttribute('hidden');
    stopCamera();
  }

  document.getElementById('take-photo-btn')?.addEventListener('click', startCamera);
  document.getElementById('capture-photo-btn')?.addEventListener('click', captureCameraPhoto);
  document.getElementById('close-camera-btn')?.addEventListener('click', stopCamera);
  document.getElementById('clear-photo-btn')?.addEventListener('click', clearProfilePhoto);
})();
