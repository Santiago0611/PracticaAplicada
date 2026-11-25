const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const EVENTO_SESION_INVALIDA = "sesion-invalida";

export async function api(ruta, { method = "GET", body } = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}${ruta}`, {
    method,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const mensaje = [data.detalle || data.error, ...Object.values(data.errores ?? {})]
      .filter(Boolean).join(" ") || "Error en la solicitud";
    const rutaPublica = ruta === "/login" || (ruta === "/usuarios" && method === "POST");
    if (res.status === 401 && !rutaPublica && token === localStorage.getItem("token")) {
      localStorage.removeItem("token");
      localStorage.removeItem("usuario");
      window.dispatchEvent(new CustomEvent(EVENTO_SESION_INVALIDA, { detail: mensaje }));
    }
    throw new Error(mensaje);
  }
  return data;
}
