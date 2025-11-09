import api from './axiosInstance';

/**
 * Obtiene el carrito activo del usuario.
 * Si no existe, se crea automáticamente.
 */
export const getCarrito = () => api.get('/carrito/');

/**
 * Agrega un curso al carrito.
 * @param {number} carritoId - ID del carrito activo
 * @param {number} cursoId - ID del curso a agregar
 */
export const agregarCursoCarrito = (carritoId, cursoId) =>
  api.post(`/carrito/${carritoId}/agregar/`, { curso_id: cursoId });

/**
 * Quita un curso del carrito.
 * @param {number} carritoId - ID del carrito activo
 * @param {number} cursoId - ID del curso a quitar
 */
export const quitarCursoCarrito = (carritoId, cursoId) =>
  api.post(`/carrito/${carritoId}/quitar/`, { curso_id: cursoId });

/**
 * Vacía todo el carrito.
 * @param {number} carritoId - ID del carrito activo
 */
export const vaciarCarrito = (carritoId) =>
  api.post(`/carrito/${carritoId}/vaciar/`);

/**
 * Hace checkout del carrito: crea el pedido e inscribe al usuario en los cursos.
 * @param {number} carritoId - ID del carrito activo
 */
export const checkoutCarrito = (carritoId) =>
  api.post(`/carrito/${carritoId}/checkout/`);

// Nota: función alternativa que crea la preferencia y luego intenta vaciar
// el carrito en el servidor para mantener front/back sincronizados.
export const checkoutAndVaciar = async (carritoId) => {
  // Crear la preferencia de pago
  const response = await api.post(`/carrito/${carritoId}/checkout/`);

  // Intentar vaciar el carrito en el servidor (no es crítico si falla)
  try {
    await api.post(`/carrito/${carritoId}/vaciar/`);
  } catch (err) {
    // Registro suave: no interrumpimos la respuesta de la preferencia
    // porque la redirección de pago puede venir a continuación.
    // El frontend también vaciará la vista de todos modos.
    // eslint-disable-next-line no-console
    console.warn('No se pudo vaciar el carrito en el servidor:', err);
  }

  return response;
};
