import React, { useState } from "react";

function Login({ onLogin }) {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");

  const formularioValido =
    correo.trim() !== "" &&
    contrasena.trim() !== "" &&
    correo.includes("@");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formularioValido) return;

    // Aquí luego conectas la API real
    if (correo === "profesor@memoreto.com" && contrasena === "1234") {
      onLogin();
    } else {
      alert("Credenciales incorrectas");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Dashboard Memoreto</h1>
        <p>Inicia sesión para consultar el rendimiento de los alumnos.</p>

        <form onSubmit={handleSubmit}>
          <label>Correo</label>
          <input
            type="email"
            placeholder="profesor@memoreto.com"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
          />

          <label>Contraseña</label>
          <input
            type="password"
            placeholder="Ingresa tu contraseña"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
          />

          <button type="submit" disabled={!formularioValido}>
            Iniciar sesión
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;