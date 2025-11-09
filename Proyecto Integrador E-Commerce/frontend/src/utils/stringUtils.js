export function formatPrice(price) {
  const precioNum = parseFloat(price);
  return precioNum.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 2,
  });
}
