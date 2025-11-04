  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const imagenBase64 = document.getElementById('imagen_base64');

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(err => {
      alert("No se pudo acceder a la cámara: " + err);
    });

  function capturarFoto() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataURL = canvas.toDataURL('image/jpeg', 0.6); // Comprimida
    imagenBase64.value = dataURL;
    document.getElementById("preview").src = dataURL;
  }