document.addEventListener("DOMContentLoaded", () => {
    // Campos del DOM
    const inputFecha = document.getElementById("id_fecha_hora_inicio");
    const inputPersonas = document.getElementById("id_num_personas");
    const inputMesaId = document.getElementById("id_mesa_seleccionada");
    const inputMesaNombre = document.getElementById("inputMesaNombre");
    const btnSubmitReserva = document.getElementById("btnSubmitReserva");

    // Estado inicial
    let mesaSeleccionadaId = inputMesaId?.value || null;

    async function actualizarDisponibilidad() {
        const fecha = inputFecha?.value;
        const numPersonas = inputPersonas?.value;

        // SANITIZACIÓN ESTRICTA: Reset visual si faltan datos
        if (!fecha || !numPersonas) {
            document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
                const figura = mesaG.querySelector(".mesa-figura");
                mesaG.dataset.disponible = "false";
                mesaG.classList.remove("mesa-ocupada");
                mesaG.classList.add("mesa-libre");
                
                figura.classList.remove("fill-success", "fill-danger", "fill-disabled");
                figura.classList.add("fill-primary");
            });
            limpiarSeleccion();
            return;
        }

        // CRÍTICO: Se mantiene RESERVA_ID para no solapar la reserva consigo misma
        const url = `${URL_DISPONIBILIDAD}?fecha_hora_inicio=${encodeURIComponent(fecha)}&num_personas=${encodeURIComponent(numPersonas)}&reserva_id=${encodeURIComponent(RESERVA_ID)}`;

        try {
            const respuesta = await fetch(url);
            const datos = await respuesta.json();

            if (!datos.ok) return;

            const mesasDisponibles = datos.mesas_disponibles.map(String);

            document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
                const figura = mesaG.querySelector(".mesa-figura");
                const mesaId = mesaG.dataset.id;

                // Limpieza de estado anterior
                figura.classList.remove("fill-primary", "fill-success", "fill-danger", "fill-disabled");
                mesaG.classList.remove("mesa-libre", "mesa-ocupada");

                if (mesasDisponibles.includes(mesaId)) {
                    mesaG.dataset.disponible = "true";
                    mesaG.classList.add("mesa-libre");
                    
                    // Si además es la mesa seleccionada, se muestra verde
                    if (mesaId === mesaSeleccionadaId) {
                        figura.classList.add("fill-success");
                    } else {
                        figura.classList.add("fill-primary");
                    }
                } else {
                    mesaG.dataset.disponible = "false";
                    mesaG.classList.add("mesa-ocupada");
                    figura.classList.add("fill-danger");
                }
            });

            // Si la mesa seleccionada previamente choca con los nuevos parámetros, se purga
            if (mesaSeleccionadaId && !mesasDisponibles.includes(mesaSeleccionadaId)) {
                limpiarSeleccion();
            }

        } catch (error) {
            console.error("Error crítico de red al consultar disponibilidad:", error);
        }
    }

    function limpiarSeleccion() {
        mesaSeleccionadaId = null;
        if (inputMesaId) inputMesaId.value = "";
        if (inputMesaNombre) inputMesaNombre.value = "Ninguna seleccionada (Elige una mesa en el plano)";
        if (btnSubmitReserva) btnSubmitReserva.disabled = true;
    }

    document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
        mesaG.addEventListener("click", () => {
            // BLOQUEO: Evitar interacciones inválidas
            if (!inputFecha.value) {
                alert("Debes establecer una fecha y hora antes de seleccionar una mesa.");
                inputFecha.focus();
                return;
            }

            if (mesaG.dataset.disponible !== "true") {
                return;
            }

            // Las mesas disponibles vuelven a color azul
            document.querySelectorAll(".mesa-figura").forEach(figura => {
                if (!figura.classList.contains("fill-danger")) {
                    figura.classList.remove("fill-success");
                    figura.classList.add("fill-primary");
                }
            });

            // La nueva mesa seleccionada se muestra en verde
            const figura = mesaG.querySelector(".mesa-figura");
            figura.classList.remove("fill-primary");
            figura.classList.add("fill-success");

            // Guardamos el ID en el formulario
            mesaSeleccionadaId = mesaG.dataset.id;
            inputMesaId.value = mesaSeleccionadaId;

            const nombreMesa = mesaG.querySelector("tspan").textContent.trim();
            inputMesaNombre.value = `${nombreMesa} (Cap: ${mesaG.dataset.capacidad} pers.)`;

            if (btnSubmitReserva) btnSubmitReserva.disabled = false;
        });
    });

    // EVENTOS ROBUSTOS
    ['change', 'input', 'blur'].forEach(evt => {
        if (inputFecha) inputFecha.addEventListener(evt, actualizarDisponibilidad);
    });
    
    ['input', 'change'].forEach(evt => {
        if (inputPersonas) inputPersonas.addEventListener(evt, actualizarDisponibilidad);
    });

    // Check de carga inicial
    actualizarDisponibilidad();
});