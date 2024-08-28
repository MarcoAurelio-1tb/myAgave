document.addEventListener("DOMContentLoaded", function() {
    loadTrabajadoresChart();
    loadCamposChart(); // Suponiendo que estas funciones están definidas para cargar gráficas

    // Función para cargar campos en selects
    function loadCamposToSelect(selectId) {
        fetch('/api/campos-select')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Seleccione un Campo</option>'; // Opción predeterminada
            data.forEach(item => {
                let option = new Option('Campo ' + item.idCampo, item.idCampo); // Texto visible, valor del option
                select.add(option);
            });
        })
        .catch(error => console.error('Error al cargar los campos:', error));
    }

    // Cargar campos en el select de vehículos
    loadCamposToSelect('campo-select');

    // Cargar campos en el select de surcos
    loadCamposToSelect('campo-select-surcos');
});


function loadTrabajadoresChart() {
    fetch('/api/trabajadores')
    .then(response => response.json())
    .then(data => {
        const trabajadoresLabels = data.map(item => item[1]);
        const trabajadoresHorasTrabajadas = data.map(item => item[4]);
        const trabajadoresHorasExtras = data.map(item => item[5]);

        // Datos para la gráfica
        var trabajadoresData = {
            labels: trabajadoresLabels,
            datasets: [{
                label: 'Horas Trabajadas',
                data: trabajadoresHorasTrabajadas,
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            },
            {
                label: 'Horas Extras',
                data: trabajadoresHorasExtras,
                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        };

        // Inicializar la gráfica
        var ctx = document.getElementById('trabajadoresChart').getContext('2d');
        var trabajadoresChart = new Chart(ctx, {
            type: 'bar',
            data: trabajadoresData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });
}

function loadCamposChart() {
    fetch('/api/campos')
    .then(response => response.json())
    .then(data => {
        const camposLabels = data.map(item => "Campo " + item.idCampo);
        const agavesPlantados = data.map(item => item.agavesPlantados);
        const maxAgaves = data.map(item => item.maxAgaves);

        // Datos para la gráfica
        var camposData = {
            labels: camposLabels,
            datasets: [{
                label: 'Agaves Plantados',
                data: agavesPlantados,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            },
            {
                label: 'Capacidad Máxima',
                data: maxAgaves,
                backgroundColor: 'rgba(255, 206, 86, 0.7)',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1
            }]
        };

        // Inicializar la gráfica
        var ctx = document.getElementById('camposChart').getContext('2d');
        var camposChart = new Chart(ctx, {
            type: 'bar',
            data: camposData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });
}


function showSection(sectionId) {
    const sections = ['trabajadores', 'vehiculos', 'herramientas', 'campos', 'insumos'];
    sections.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            if (id === sectionId) {
                element.style.display = 'block'; // Muestra la sección seleccionada
            } else {
                element.style.display = 'none'; // Oculta las otras secciones
            }
        }
    });
}


document.getElementById('tu-boton-vehiculos').addEventListener('click', function() {
    showSection('vehiculos'); // Asegúrate de que este sea el ID correcto para la sección vehículos
    fetch('/api/campos-select')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('enCampo'); // Asegúrate de que este sea el ID correcto del elemento select en tu HTML
            select.innerHTML = '<option value="">Seleccione un Campo</option>'; // Asegúrate de mantener la opción predeterminada
            data.forEach(campo => {
                const option = document.createElement('option');
                option.value = campo.idCampo;
                option.textContent = 'Campo ' + campo.idCampo;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error al obtener los campos:', error);
        });
});
document.getElementById2('tu-boton-vehiculos').addEventListener('click', function() {
    showSection('vehiculos'); // Asegúrate de que este sea el ID correcto para la sección vehículos
    fetch('/api/campos-select')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('enCampo'); // Asegúrate de que este sea el ID correcto del elemento select en tu HTML
            select.innerHTML = '<option value="">Seleccione un Campo</option>'; // Asegúrate de mantener la opción predeterminada
            data.forEach(campo => {
                const option = document.createElement('option');
                option.value = campo.idCampo;
                option.textContent = 'Campo ' + campo.idCampo;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error al obtener los campos:', error);
        });
});


document.addEventListener("DOMContentLoaded", function() {
    // Escucha el evento de clic en el botón "Agave Precio"
    document.getElementById('btn-precio-agave').addEventListener('click', function(e) {
        e.preventDefault(); // Previene la navegación a una nueva página
        // Llama a la función para obtener y almacenar el precio
        obtenerYMostrarPrecioAgave();
    });
});

function obtenerYMostrarPrecioAgave() {
    // Primero, dispara la función que almacena el precio en la base de datos
    fetch('/almacenar_precio_agve')
    .then(response => response.json())
    .then(data => {
        if (data.mensaje) {
            // Si el precio se almacena correctamente, obtén el último precio y muéstralo
            fetch('/obtener_ultimo_precio_agve')
            .then(response => response.json())
            .then(data => {
                if (!data.error) {
                    // Actualiza el contenido en la página con el nuevo precio
                    document.getElementById('precio-agve').innerHTML =
                        'Último precio del AGVE: $' + data.precio.toFixed(2) +
                        ' (Actualizado en: ' + data.fecha + ')';
                } else {
                    document.getElementById('precio-agve').innerHTML = data.error;
                }
            });
        } else {
            document.getElementById('precio-agve').innerHTML = 'Error al almacenar el precio del AGVE.';
        }
    });
}
