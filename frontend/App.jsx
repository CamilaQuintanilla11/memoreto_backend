import React, { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import "./styles.css";

function App() {
  const [logueado, setLogueado] = useState(false);

  return (
    <>
      {logueado ? (
        <Dashboard />
      ) : (
        <Login onLogin={() => setLogueado(true)} />
      )}
    </>
  );
}

export default App;