import React, { useEffect, useState } from "react";
import Plotly from "plotly.js-dist-min";

function Dashboard() {
  const [datos, setDatos] = useState(null);

  useEffect(() => {
    cargarGraficas();
  }, []);

  const cargarGraficas = async () => {
    try {
      const response = await fetch("https://memoreto.aldo1207.uber.space/api/graficas");
      const data = await response.json();

      if (data.success) {
        setDatos(data);

        Plotly.newPlot(
          "grafica-tiempo",
          [
            {
              labels: data.niveles,
              values: data.tiempos,
              type: "pie",
            },
          ],
          {
            title: "Tiempo Promedio por Nivel",
          }
        );

        Plotly.newPlot(
          "grafica-score",
          [
            {
              x: data.niveles,
              y: data.scores,
              type: "bar",
            },
          ],
          {
            title: "Puntaje Promedio por Nivel",
          }
        );
      }
    } catch (error) {
      console.error("Error al cargar gráficas:", error);
    }
  };

  const totalNiveles = datos?.niveles?.length || 0;
  const promedioTiempo = datos?.tiempos?.length
    ? (datos.tiempos.reduce((a, b) => a + b, 0) / datos.tiempos.length).toFixed(2)
    : "--";
  const promedioScore = datos?.scores?.length
    ? (datos.scores.reduce((a, b) => a + b, 0) / datos.scores.length).toFixed(2)
    : "--";

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard Memoreto</h1>
        <p>Resumen de rendimiento de los alumnos en los memoretos.</p>
      </header>

      <section className="cards-section">
        <div className="card">
          <h3>Total de niveles</h3>
          <p>{totalNiveles}</p>
        </div>

        <div className="card">
          <h3>Tiempo promedio</h3>
          <p>{promedioTiempo} s</p>
        </div>

        <div className="card">
          <h3>Score promedio</h3>
          <p>{promedioScore}</p>
        </div>
      </section>

      <section className="graficas-section">
        <div className="grafica-box">
          <div id="grafica-tiempo"></div>
          <p><strong>Autor:</strong> Aldo</p>
          <p>
            Esta gráfica de pastel muestra la distribución porcentual del tiempo
            promedio que los alumnos invierten en cada nivel.
          </p>
        </div>

        <div className="grafica-box">
          <div id="grafica-score"></div>
          <p><strong>Autor:</strong> Ariel</p>
          <p>
            Esta gráfica de barras compara el puntaje promedio obtenido por los
            estudiantes según el nivel de dificultad.
          </p>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;