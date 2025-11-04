document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const preview = document.getElementById("preview");
  const tomarFoto = document.getElementById("tomarFoto");
  const borrarFoto = document.getElementById("borrarFoto");
  const evidenciaInput = document.getElementById("evidenciaInput");

  // Iniciar cámara
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(err => console.error("Error al acceder a la cámara:", err));

  // Tomar foto
  tomarFoto.addEventListener("click", () => {
    if (!video.videoWidth || !video.videoHeight) {
      alert("La cámara aún no está lista, intenta de nuevo.");
      return;
    }

    const maxSize = 800;
    const ctx = canvas.getContext("2d");

    let w = video.videoWidth;
    let h = video.videoHeight;

    if (w > h && w > maxSize) {
      h = Math.round((h * maxSize) / w);
      w = maxSize;
    } else if (h >= w && h > maxSize) {
      w = Math.round((w * maxSize) / h);
      h = maxSize;
    }

    canvas.width = w;
    canvas.height = h;
    ctx.drawImage(video, 0, 0, w, h);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.8);

    preview.src = dataUrl;
    preview.style.display = "block";
    video.style.display = "none";

    evidenciaInput.value = dataUrl;
  });

  // Borrar foto
  borrarFoto.addEventListener("click", () => {
    preview.src = "";
    preview.style.display = "none";
    video.style.display = "block";
    evidenciaInput.value = "";
  });
});
