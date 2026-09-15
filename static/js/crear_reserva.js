document.addEventListener("DOMContentLoaded", () => {
    let mesaSeleccionadaId = null;

    const inputMesaId = document.getElementById("id_mesa_seleccionada");
    const inputMesaNombre = document.getElementById("inputMesaNombre");
    const btnSubmitReserva = document.getElementById("btnSubmitReserva");

    const inputFecha = document.getElementById("id_fecha_hora_inicio");
    const inputPersonas = document.getElementById("id_num_personas");
    const errorContainer = document.getElementById("errorNumPersonas");

    function purgarPlano() {
        document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
            const figura = mesaG.querySelector(".mesa-figura");
            mesaG.dataset.disponible = "false";
            mesaG.classList.remove("mesa-ocupada");
            mesaG.classList.add("mesa-libre");
            
            figura.classList.remove("fill-success", "fill-danger", "fill-disabled");
            figura.classList.add("fill-primary");
        });
        limpiarSeleccion();
    }

    async function actualizarDisponibilidad() {
        const fecha = inputFecha?.value;
        const numPersonasStr = inputPersonas?.value;
        const numPersonas = parseInt(numPersonasStr, 10);

        // VALIDACIÓN CLIENT-SIDE: Si el número de personas es menor a 1
        if (numPersonasStr && numPersonas < 1) {
            if (errorContainer) {
                errorContainer.textContent = "El número de comensales debe ser al menos 1.";
                errorContainer.style.display = "block";
            }
            purgarPlano();
            return;
        } else {
            if (errorContainer) {
                errorContainer.style.display = "none";
                errorContainer.textContent = "";
            }
        }

        // SANITIZACIÓN ESTRICTA: Si faltan datos, purgar el plano y bloquear la UI
        if (!fecha || !numPersonasStr) {
            purgarPlano();
            return;
        }

        const url = `${URL_DISPONIBILIDAD}?fecha_hora_inicio=${encodeURIComponent(fecha)}&num_personas=${encodeURIComponent(numPersonas)}`;

        try {
            const respuesta = await fetch(url);
            
            if (!respuesta.ok) {
                purgarPlano();
                return;
            }

            const datos = await respuesta.json();
            if (!datos.ok) return;

            const mesasDisponibles = datos.mesas_disponibles.map(String);

            document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
                const figura = mesaG.querySelector(".mesa-figura");
                const mesaId = mesaG.dataset.id;

                // Limpieza de estados residuales
                figura.classList.remove("fill-primary", "fill-success", "fill-danger", "fill-disabled");
                mesaG.classList.remove("mesa-libre", "mesa-ocupada");

                if (mesasDisponibles.includes(mesaId)) {
                    mesaG.dataset.disponible = "true";
                    mesaG.classList.add("mesa-libre");
                    
                    // Restaurar el verde si esta mesa ya estaba seleccionada
                    if (mesaId === mesaSeleccionadaId) {
                        figura.classList.add("fill-success");
                    } else {
                        figura.classList.add("fill-primary");
                    }
                } else {
                    // Mesa solapada en ese horario o sin capacidad
                    mesaG.dataset.disponible = "false";
                    mesaG.classList.add("mesa-ocupada");
                    figura.classList.add("fill-danger");
                }
            });

            // Si la mesa que el usuario tenía seleccionada colisiona tras cambiar la hora, expulsarlo
            if (mesaSeleccionadaId && !mesasDisponibles.includes(mesaSeleccionadaId)) {
                limpiarSeleccion();
            }

        } catch (error) {
            console.error("Fallo de red al consultar disponibilidad AJAX:", error);
        }
    }

    function limpiarSeleccion() {
        mesaSeleccionadaId = null;
        if (inputMesaId) inputMesaId.value = "";
        if (inputMesaNombre) inputMesaNombre.value = "Ninguna seleccionada (Elige en el plano)";
        if (btnSubmitReserva) btnSubmitReserva.disabled = true;
    }

    document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
        mesaG.addEventListener("click", () => {
            // CONTROL DE FLUJO: Impedir tocar el plano sin definir fecha
            if (!inputFecha.value) {
                alert("Debes establecer una fecha y hora antes de seleccionar una mesa.");
                inputFecha.focus();
                return;
            }

            if (mesaG.dataset.disponible !== "true") {
                return;
            }

            // Resetear el resto de mesas libres a azul
            document.querySelectorAll(".mesa-figura").forEach(figura => {
                if (!figura.classList.contains("fill-danger")) {
                    figura.classList.remove("fill-success");
                    figura.classList.add("fill-primary");
                }
            });

            // Marcar la mesa clicada en verde
            const figura = mesaG.querySelector(".mesa-figura");
            figura.classList.remove("fill-primary");
            figura.classList.add("fill-success");

            // Persistir la selección en el formulario
            mesaSeleccionadaId = mesaG.dataset.id;
            inputMesaId.value = mesaSeleccionadaId;

            const nombreMesa = mesaG.querySelector("tspan").textContent.trim();
            inputMesaNombre.value = `${nombreMesa} (Cap: ${mesaG.dataset.capacidad} pers.)`;

            btnSubmitReserva.disabled = false;
        });
    });

    // BATERÍA DE EVENTOS: Garantiza que la petición AJAX salte en cualquier navegador
    ['change', 'input', 'blur'].forEach(evt => {
        if (inputFecha) inputFecha.addEventListener(evt, actualizarDisponibilidad);
    });
    
    ['input', 'change'].forEach(evt => {
        if (inputPersonas) inputPersonas.addEventListener(evt, actualizarDisponibilidad);
    });

    // Inicialización
    actualizarDisponibilidad();
});