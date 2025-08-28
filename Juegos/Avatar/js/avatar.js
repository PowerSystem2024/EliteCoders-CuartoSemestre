//  Estado y referencias (constantes)
const state = {
  ataqueJugador: null,
  ataqueEnemigo: null,
  vidas: { jugador: 3, enemigo: 3 },
  reglasVisibles: false,
};

const refs = {
  // Botones
  botonReglas: null,
  botonJugar: null,
  botonPersonaje: null,
  botonReiniciar: null,
  botonPunio: null,
  botonPatada: null,
  botonBarrida: null,
  // Secciones
  seccionReglas: null,
  seccionSeleccionarAtaque: null,
  seccionSeleccionarPersonaje: null,
  // Spans
  spanPersonajeJugador: null,
  spanPersonajeEnemigo: null,
  spanVidasJugador: null,
  spanVidasEnemigo: null,
  // Mensaje
  mensajePrincipal: null,
};

const inicializarElementos = () => {
  refs.botonReglas = document.getElementById("boton-reglas");
  refs.botonJugar = document.getElementById("boton-jugar");
  refs.botonPersonaje = document.getElementById("boton-personaje");
  refs.botonReiniciar = document.getElementById("boton-reiniciar");
  refs.botonPunio = document.getElementById("boton-punio");
  refs.botonPatada = document.getElementById("boton-patada");
  refs.botonBarrida = document.getElementById("boton-barrida");

  refs.seccionReglas = document.getElementById("reglas-del-juego");
  refs.seccionSeleccionarAtaque = document.getElementById("seleccionar-ataque");
  refs.seccionSeleccionarPersonaje = document.getElementById("seleccionar-personaje");

  refs.spanPersonajeJugador = document.getElementById("personaje-jugador");
  refs.spanPersonajeEnemigo = document.getElementById("personaje-enemigo");
  refs.spanVidasJugador = document.getElementById("vidas-jugador");
  refs.spanVidasEnemigo = document.getElementById("vidas-enemigo");

  // Soporte para #mensaje-principal 
  refs.mensajePrincipal =
    document.getElementById("mensaje-principal") ||
    document.getElementById("mensajes");
};

// Inicio del juego 
const iniciarJuego = () => {
  inicializarElementos();

  refs.botonReglas.addEventListener("click", mostrarReglas);
  refs.botonJugar.addEventListener("click", seleccionarPersonajeJugador);
  refs.botonPersonaje.addEventListener("click", seleccionarPersonajeJugador);
  refs.botonReiniciar.addEventListener("click", reiniciarJuego);

  refs.botonPunio.addEventListener("click", ataquePunio);
  refs.botonPatada.addEventListener("click", ataquePatada);
  refs.botonBarrida.addEventListener("click", ataqueBarrida);

  establecerEstadoInicial();
};

const establecerEstadoInicial = () => {
  refs.seccionReglas.style.display = "none";
  refs.seccionSeleccionarAtaque.style.display = "none";
  refs.seccionSeleccionarPersonaje.style.display = "block";
  state.reglasVisibles = false;
  refs.botonReiniciar.disabled = true;
  deshabilitarBotonesAtaque();
};

// UI 
const mostrarReglas = () => {
  state.reglasVisibles = !state.reglasVisibles;
  refs.seccionReglas.style.display = state.reglasVisibles ? "block" : "none";
};

const seleccionarPersonajeJugador = () => {
  refs.seccionReglas.style.display = "none";
  state.reglasVisibles = false;

  const checked = document.querySelector('input[name="personaje"]:checked');
  const personajeSeleccionado = checked?.value || checked?.id;

  if (!personajeSeleccionado) {
    alert("Selecciona un personaje");
    return;
  }

  refs.spanPersonajeJugador.innerHTML = personajeSeleccionado;
  refs.mensajePrincipal.innerHTML = `Seleccionaste al personaje ${personajeSeleccionado}`;

  seleccionarPersonajeEnemigo();
  cambiarEstadoJuegoIniciado();
};

const seleccionarPersonajeEnemigo = () => {
  const personajes = ["Zuko", "Katara", "Aang", "Toph"];
  const personajeAleatorio = personajes[Math.floor(Math.random() * personajes.length)];

  refs.spanPersonajeEnemigo.innerHTML = personajeAleatorio;
  refs.mensajePrincipal.innerHTML += `<br>El enemigo seleccionó al personaje ${personajeAleatorio}`;
};

const cambiarEstadoJuegoIniciado = () => {
  refs.botonPersonaje.disabled = true;
  refs.botonJugar.disabled = true;

  refs.botonReiniciar.disabled = false;
  habilitarBotonesAtaque();

  refs.seccionSeleccionarAtaque.style.display = "block";
  refs.seccionSeleccionarPersonaje.style.display = "none";
};

// Combate 
const numeroRandom = (min, max) =>
  Math.floor(Math.random() * (max - min + 1) + min);

const ataqueAleatorioEnemigo = () => {
  const n = numeroRandom(1, 3);
  state.ataqueEnemigo = n === 1 ? "Puño" : n === 2 ? "Patada" : "Barrida";
};

const esVictoriaJugador = () =>
  (state.ataqueJugador === "Puño" && state.ataqueEnemigo === "Barrida") ||
  (state.ataqueJugador === "Patada" && state.ataqueEnemigo === "Puño") ||
  (state.ataqueJugador === "Barrida" && state.ataqueEnemigo === "Patada");

const combatir = () => {
  let mensaje = "";

  if (state.ataqueJugador === state.ataqueEnemigo) {
    mensaje = `¡Empate! Ambos atacaron con ${state.ataqueJugador}`;
  } else if (esVictoriaJugador()) {
    state.vidas.enemigo--;
    mensaje = `¡Ganaste! Tu ${state.ataqueJugador} venció al ${state.ataqueEnemigo} del enemigo.`;
  } else {
    state.vidas.jugador--;
    mensaje = `¡Perdiste! El ${state.ataqueEnemigo} del enemigo venció a tu ${state.ataqueJugador}.`;
  }

  actualizarInterfaz(mensaje);
  verificarFinDelJuego(mensaje);
};

const actualizarInterfaz = (mensaje) => {
  refs.mensajePrincipal.innerHTML = mensaje;
  refs.spanVidasJugador.innerHTML = state.vidas.jugador;
  refs.spanVidasEnemigo.innerHTML = state.vidas.enemigo;
};

const verificarFinDelJuego = (mensaje) => {
  if (state.vidas.jugador <= 0 || state.vidas.enemigo <= 0) {
    const resultadoFinal =
      state.vidas.jugador <= 0 ? "¡Perdiste el juego!" : "¡Ganaste el juego!";
    refs.mensajePrincipal.innerHTML = `${mensaje}<br><strong>${resultadoFinal}</strong>`;
    deshabilitarBotonesAtaque();
  }
};

//  Acciones de ataque 
const ataquePunio = () => {
  state.ataqueJugador = "Puño";
  ataqueAleatorioEnemigo();
  combatir();
};

const ataquePatada = () => {
  state.ataqueJugador = "Patada";
  ataqueAleatorioEnemigo();
  combatir();
};

const ataqueBarrida = () => {
  state.ataqueJugador = "Barrida";
  ataqueAleatorioEnemigo();
  combatir();
};

// Habilitar/Deshabilitar 
const habilitarBotonesAtaque = () => {
  refs.botonPunio.disabled = false;
  refs.botonPatada.disabled = false;
  refs.botonBarrida.disabled = false;
};

const deshabilitarBotonesAtaque = () => {
  refs.botonPunio.disabled = true;
  refs.botonPatada.disabled = true;
  refs.botonBarrida.disabled = true;
};

// Reinicio 
const reiniciarJuego = () => {
  resetearVariablesJuego();
  limpiarInterfaz();
  desmarcarPersonajes();
  restaurarEstadoBotones();
  mostrarSeccionesIniciales();
};

const resetearVariablesJuego = () => {
  state.vidas.jugador = 3;
  state.vidas.enemigo = 3;
  state.ataqueJugador = null;
  state.ataqueEnemigo = null;
};

const limpiarInterfaz = () => {
  refs.spanPersonajeJugador.innerHTML = "";
  refs.spanPersonajeEnemigo.innerHTML = "";
  refs.spanVidasJugador.innerHTML = "3";
  refs.spanVidasEnemigo.innerHTML = "3";
  refs.mensajePrincipal.innerHTML = "";
};

const desmarcarPersonajes = () => {
  document
    .querySelectorAll('input[name="personaje"]')
    .forEach((input) => (input.checked = false));
};

const restaurarEstadoBotones = () => {
  refs.botonPersonaje.disabled = false;
  refs.botonJugar.disabled = false;
  refs.botonReiniciar.disabled = true;
  deshabilitarBotonesAtaque();
};

const mostrarSeccionesIniciales = () => {
  refs.seccionSeleccionarPersonaje.style.display = "block";
  refs.seccionSeleccionarAtaque.style.display = "none";
  refs.seccionReglas.style.display = "none";
  state.reglasVisibles = false;
};

// Boot 
window.addEventListener("load", () => {
  iniciarJuego();

  // Permite seleccionar el radio al hacer click 
  document.querySelectorAll(".opcion-personaje").forEach((div) => {
    div.addEventListener("click", function () {
      const radio = div.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        radio.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
  });
});
