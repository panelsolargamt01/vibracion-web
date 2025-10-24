const form = document.getElementById("formulario");
const progreso = document.getElementById("progreso");
const barra = progreso.querySelector(".barra");
const resultado = document.getElementById("resultado");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultado.innerHTML = "";
  progreso.classList.remove("oculto");
  barra.style.width = "0%";

  const formData = new FormData(form);
  barra.style.width = "40%";

  const res = await fetch("/procesar", { method: "POST", body: formData });
  barra.style.width = "90%";

  const data = await res.json();
  barra.style.width = "100%";
  setTimeout(() => progreso.classList.add("oculto"), 600);

  if (data.error) {
    resultado.innerHTML = `<p style="color: #ef4444;">❌ ${data.error}</p>`;
  } else {
    resultado.innerHTML = `<p>${data.mensaje}</p>`;

    // Descargar los tres audios automáticamente
    data.archivos.forEach(a => {
      const link = document.createElement("a");
      link.href = a.url;
      link.download = a.nombre;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Mostrar enlace en la web también
      const infoLink = document.createElement("a");
      infoLink.href = a.url;
      infoLink.download = a.nombre;
      infoLink.className = "audio-link";
      infoLink.textContent = `🎵 Descargar ${a.nombre}`;
      resultado.appendChild(infoLink);
    });
  }
});
