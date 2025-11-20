# PixelPress - Blog de videojuegos

Repositorio listo para usarse como demo de blog/landing para contenido de videojuegos. Incluye modo de artículos estándar y modo "Análisis" con ficha automática, panel de redactor protegido por contraseña y sistema de comentarios en `localStorage`.

## Estructura

```
src/
├─ index.html      # Página principal con listado y acceso al panel
├─ article.html    # Vista de detalle con comentarios
├─ styles.css      # Estilos responsive
├─ main.js         # Gestión de artículos y comentarios
├─ admin.js        # Autenticación simple y creación de entradas
└─ analysis.js     # Plantilla automática para modo análisis
```

## Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone <url> pixelpress
   cd pixelpress
   ```
2. No requiere dependencias externas. Abre `src/index.html` directamente en el navegador o sirve la carpeta con cualquier servidor estático:
   ```bash
   npx serve src
   ```

## Uso

- **Listado y lectura**: los artículos se cargan desde `localStorage`. El botón "Restaurar demo" repone ejemplos iniciales.
- **Panel de redactor**: abre "Panel redactor" y usa la contraseña `pressstart`. Al crear un artículo de tipo "Análisis" se genera automáticamente:
  - Ficha técnica (plataforma, estudio, género, modos)
  - Pros y contras
  - Resumen y comparativa
  - Valoración global y puntuación Metacritic simulada
  - Capturas (si añades URLs separadas por comas)
- **Comentarios**: en `article.html`, los mensajes se guardan por ID de artículo en `localStorage`.

## Personalización

- Ajusta estilos en `src/styles.css` (colores, gradientes, breakpoints).
- Cambia la contraseña del panel modificando `ADMIN_PASSWORD` en `src/admin.js`.
- Amplía el esquema de artículos desde `saveArticles`/`getArticles` en `src/main.js` o añade nuevos campos en el formulario.

## Notas

- El almacenamiento es local por navegador; limpiar datos o usar "Restaurar demo" rehace los ejemplos.
- Las puntuaciones y comparativas del modo análisis son ficticias y se recalculan al crear cada artículo.
