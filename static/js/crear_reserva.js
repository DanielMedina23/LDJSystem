document.addEventListener("DOMContentLoaded", () => {
    let mesaSeleccionadaId = null;

    const inputMesaId = document.getElementById("id_mesa_seleccionada");
    const inputMesaNombre = document.getElementById("inputMesaNombre");
    const btnSubmitReserva = document.getElementById("btnSubmitReserva");

    const inputFecha = document.getElementById("id_fecha_hora_inicio");
    const inputPersonas = document.getElementById("id_num_personas");

    async function actualizarDisponibilidad() {
        const fecha = inputFecha.value;
        const numPersonas = inputPersonas.value;

        if (!fecha || !numPersonas) {
            return;
        }

        const url = `${URL_DISPONIBILIDAD}?fecha_hora_inicio=${encodeURIComponent(fecha)}&num_personas=${encodeURIComponent(numPersonas)}`;

        const respuesta = await fetch(url);
        const datos = await respuesta.json();

        if (!datos.ok) {
            return;
        }

        const mesasDisponibles = datos.mesas_disponibles.map(String);

        document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
            const figura = mesaG.querySelector(".mesa-figura");
            const mesaId = mesaG.dataset.id;

            figura.classList.remove(
                "fill-primary",
                "fill-success",
                "fill-danger",
                "fill-disabled"
            );

            if (mesasDisponibles.includes(mesaId)) {
                mesaG.dataset.disponible = "true";
                figura.classList.add("fill-primary");
            } else {
                mesaG.dataset.disponible = "false";
                figura.classList.add("fill-danger");
            }
        });

        // Si la mesa que estaba seleccionada deja de estar disponible,
        // limpiamos la selección.
        if (
            mesaSeleccionadaId &&
            !mesasDisponibles.includes(mesaSeleccionadaId)
        ) {
            mesaSeleccionadaId = null;
            inputMesaId.value = "";
            inputMesaNombre.value = "Ninguna seleccionada (Elige en el plano)";
            btnSubmitReserva.disabled = true;
        }
    }

    document.querySelectorAll(".mesa-elemento").forEach(mesaG => {
        mesaG.addEventListener("click", () => {
            if (mesaG.dataset.disponible !== "true") {
                return;
            }

            document.querySelectorAll(".mesa-figura").forEach(figura => {
                if (!figura.classList.contains("fill-danger")) {
                    figura.classList.remove("fill-success");
                    figura.classList.add("fill-primary");
                }
            });

            const figura = mesaG.querySelector(".mesa-figura");

            figura.classList.remove("fill-primary");
            figura.classList.add("fill-success");

            mesaSeleccionadaId = mesaG.dataset.id;
            inputMesaId.value = mesaSeleccionadaId;

            const nombreMesa = mesaG.querySelector("tspan").textContent;

            inputMesaNombre.value =
                `${nombreMesa} (Cap: ${mesaG.dataset.capacidad} pers.)`;

            btnSubmitReserva.disabled = false;
        });
    });

    inputFecha.addEventListener("change", actualizarDisponibilidad);
    inputPersonas.addEventListener("input", actualizarDisponibilidad);

    actualizarDisponibilidad();
});