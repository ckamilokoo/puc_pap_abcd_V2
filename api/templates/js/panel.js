// Este evento asegura que el código JavaScript se ejecute solo después de que el DOM se haya cargado completamente.
document.addEventListener("DOMContentLoaded", function () {
  // Se define un array de objetos llamado 'casos', donde cada objeto representa un caso con sus propiedades.
  const casos = [
    {
      nombre: "Caso Argelia", // Nombre del caso
      lugar: "Lugar 1", // Lugar del evento
      tipo: "Tipo 1", // Tipo de evento traumático
      situacion: "Problema 1", // Situación problemática
    },
    {
      nombre: "Caso Ramon",
      lugar: "Lugar 2",
      tipo: "Tipo 2",
      situacion: "Problema 2",
    },
    {
      nombre: "Caso Luis",
      lugar: "Lugar 3",
      tipo: "Tipo 3",
      situacion: "Problema 3",
    },
  ];

  // Se obtiene la referencia del elemento del DOM con el id 'listaCasos'.
  const listaCasos = document.getElementById("listaCasos");

  // Función que actualiza la lista de casos en el DOM.
  function actualizarListaCasos() {
    listaCasos.innerHTML = ""; // Se vacía el contenido de 'listaCasos'.
    casos.forEach((caso, index) => {
      // Se itera sobre cada caso en el array 'casos'.
      const li = document.createElement("li"); // Se crea un nuevo elemento <li>.
      li.textContent = caso.nombre; // Se establece el texto del <li> como el nombre del caso.
      const btn = document.createElement("button"); // Se crea un nuevo botón.
      btn.textContent = "+"; // Se establece el texto del botón como '+'.
      // Se añade un evento onclick al botón que llama a la función 'mostrarCaso' con el índice del caso.
      btn.onclick = () => mostrarCaso(index);
      li.appendChild(btn); // Se añade el botón al elemento <li>.
      listaCasos.appendChild(li); // Se añade el elemento <li> a la lista de casos en el DOM.
    });
  }

  // Función que muestra los detalles de un caso específico.
  function mostrarCaso(index) {
    const caso = casos[index]; // Se obtiene el caso correspondiente al índice dado.
    const detalleCaso = document.getElementById("detalleCaso"); // Se obtiene la referencia del elemento con el id 'detalleCaso'.
    // Se establece el contenido HTML de 'detalleCaso' con los detalles del caso y un botón para copiar los datos.
    detalleCaso.innerHTML = `
            <input type="text" value="${caso.nombre}" readonly>
            <input type="text" value="${caso.lugar}" readonly>
            <input type="text" value="${caso.tipo}" readonly>
            <input type="text" value="${caso.situacion}" readonly>
            <button onclick="copiarDatos(${index})">Copiar datos</button>
            <button id="simular">Simular Caso</button>
        `;
    // Se muestra el contenedor '.caso' cambiando su estilo de display a 'block'.
    document.querySelector(".caso").style.display = "block";
  }

  // Se define una función global que copia los datos del caso seleccionado al formulario.
  window.copiarDatos = function (index) {
    const caso = casos[index]; // Se obtiene el caso correspondiente al índice dado.
    // Se establecen los valores de los campos del formulario con los datos del caso.
    document.getElementById("nombreCaso").value = caso.nombre;
    document.getElementById("lugarEvento").value = caso.lugar;
    document.getElementById("tipoEvento").value = caso.tipo;
    document.getElementById("situacionProblema").value = caso.situacion;
  };

  // Se define una función global que crea un nuevo caso a partir de los datos del formulario.
  window.crearNuevoCaso = function () {
    // Se crea un nuevo objeto 'nuevoCaso' con los valores de los campos del formulario.
    const nuevoCaso = {
      nombre: document.getElementById("nombreCaso").value,
      lugar: document.getElementById("lugarEvento").value,
      tipo: document.getElementById("tipoEvento").value,
      situacion: document.getElementById("situacionProblema").value,
    };

    casos.push(nuevoCaso); // Se añade el nuevo caso al array 'casos'.
    actualizarListaCasos(); // Se actualiza la lista de casos en el DOM.
    const nuevoCasoGenerado = document.getElementById("nuevoCasoGenerado"); // Se obtiene la referencia del elemento 'nuevoCasoGenerado'.
    // Se establece el contenido de 'nuevoCasoGenerado' con un mensaje indicando que el caso se creó correctamente.
    nuevoCasoGenerado.textContent = `Caso ${nuevoCaso.nombre} creado correctamente.`;
    document.querySelector(".cardbody").style.display = "block"; // Se muestra el contenedor '.cardbody'.

    // Se vacían los campos del formulario.
    document.getElementById("nombreCaso").value = "";
    document.getElementById("lugarEvento").value = "";
    document.getElementById("tipoEvento").value = "";
    document.getElementById("situacionProblema").value = "";
  };

  actualizarListaCasos(); // Se llama a la función para actualizar la lista de casos cuando se carga la página.
});
