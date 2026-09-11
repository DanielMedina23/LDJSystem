document.addEventListener("DOMContentLoaded", () => {

    // Campos utilizados para consultar la disponibilidad
    const inputFecha = document.getElementById("id_fecha_hora_inicio");
    const inputPersonas = document.getElementById("id_num_personas");

    // Campos utilizados para guardar y mostrar la mesa seleccionada
    const inputMesaId = document.getElementById("id_mesa_seleccionada");
    const inputMesaNombre = document.getElementById("inputMesaNombre");

    // Botón que actualiza la reserva
    const btnSubmitReserva = document.getElementById("btnSubmitReserva");

    // Al editar, comenzamos con la mesa que ya tiene asignada la reserva
    let mesaSeleccionadaId = inputMesaId.value || null;


    // Consulta al servidor qué mesas están disponibles
    async function actualizarDisponibilidad() {

        const fecha = inputFecha.value;
        const numPersonas = inputPersonas.value;

        // No podemos consultar disponibilidad sin estos datos
        if (!fecha || !numPersonas) {
            return;
        }

        const url =
            `${URL_DISPONIBILIDAD}` +
            `?fecha_hora_inicio=${encodeURIComponent(fecha)}` +
            `&num_personas=${encodeURIComponent(numPersonas)}` +
            `&reserva_id=${encodeURIComponent(RESERVA_ID)}`;

        try {

            const respuesta = await fetch(url);
            const datos = await respuesta.json();

            if (!datos.ok) {
                return;
            }

            // Convertimos los ID a String porque dataset devuelve Strings
            const mesasDisponibles = datos.mesas_disponibles.map(String);


            // Recorremos todas las mesas del plano
            document.querySelectorAll(".mesa-elemento").forEach(mesaG => {

                const figura = mesaG.querySelector(".mesa-figura");
                const mesaId = mesaG.dataset.id;

                // Limpiamos los colores anteriores
                figura.classList.remove(
                    "fill-primary",
                    "fill-success",
                    "fill-danger",
                    "fill-disabled"
                );


                // Mesa disponible
                if (mesasDisponibles.includes(mesaId)) {

                    mesaG.dataset.disponible = "true";

                    // Si además es la mesa seleccionada, se muestra verde
                    if (mesaId === mesaSeleccionadaId) {
                        figura.classList.add("fill-success");
                    } else {
                        figura.classList.add("fill-primary");
                    }

                // Mesa no disponible
                } else {

                    mesaG.dataset.disponible = "false";
                    figura.classList.add("fill-danger");

                }

            });


            /*
             * Si la mesa que tenía seleccionada deja de estar disponible
             * por un cambio de fecha o número de personas, se elimina
             * la selección para obligar al empleado a escoger otra.
             */
            if (
                mesaSeleccionadaId &&
                !mesasDisponibles.includes(mesaSeleccionadaId)
            ) {

                mesaSeleccionadaId = null;

                inputMesaId.value = "";

                inputMesaNombre.value =
                    "Ninguna seleccionada (Elige una mesa en el plano)";

                if (btnSubmitReserva) {
                    btnSubmitReserva.disabled = true;
                }
            }

        } catch (error) {

            console.error(
                "Error al consultar la disponibilidad de las mesas:",
                error
            );

        }
    }


    // Permitimos seleccionar una mesa haciendo clic en el plano
    document.querySelectorAll(".mesa-elemento").forEach(mesaG => {

        mesaG.addEventListener("click", () => {

            // No permitimos seleccionar una mesa ocupada
            if (mesaG.dataset.disponible !== "true") {
                return;
            }


            // Las mesas disponibles vuelven a color azul
            document.querySelectorAll(".mesa-elemento").forEach(otraMesa => {

                const figura = otraMesa.querySelector(".mesa-figura");

                if (otraMesa.dataset.disponible === "true") {
                    figura.classList.remove("fill-success");
                    figura.classList.add("fill-primary");
                }

            });


            // La nueva mesa seleccionada se muestra en verde
            const figura = mesaG.querySelector(".mesa-figura");

            figura.classList.remove("fill-primary");
            figura.classList.add("fill-success");


            // Guardamos el ID de la nueva mesa
            mesaSeleccionadaId = mesaG.dataset.id;
            inputMesaId.value = mesaSeleccionadaId;


            // Mostramos al usuario qué mesa seleccionó
            const nombreMesa = mesaG.querySelector("tspan").textContent.trim();

            inputMesaNombre.value =
                `${nombreMesa} (Cap: ${mesaG.dataset.capacidad} pers.)`;


            if (btnSubmitReserva) {
                btnSubmitReserva.disabled = false;
            }

        });

    });


    // Volvemos a calcular las mesas si cambia la fecha
    inputFecha.addEventListener(
        "change",
        actualizarDisponibilidad
    );

    // También si cambia el número de personas
    inputPersonas.addEventListener(
        "input",
        actualizarDisponibilidad
    );


    // Comprobamos disponibilidad al entrar a editar la reserva
    actualizarDisponibilidad();

});