# 🧠 Asistente Inteligente para Agricultura de Precisión - Agrobot

Este proyecto es una herramienta de asistencia agrícola basada en inteligencia artificial, diseñada para ayudar a agricultores y profesionales del agro a tomar decisiones informadas sobre fertilización, tipos de suelo y requerimientos nutricionales de distintos cultivos.

## 🚀 Funcionalidades Principales

- 🧑‍🌾 **Asistente inteligente (chatbot)** que responde consultas relacionadas con cultivos y suelos.
- 🧪 Consulta de **requerimientos nutricionales óptimos** para más de 30 cultivos.
- 🌱 Identificación de brechas nutricionales según el análisis de suelo ingresado.
- 📊 Visualización y manejo de datos de suelos globales y nutrientes.
- ⚙️ Preparado para despliegue en Heroku.

## 📁 Estructura del Proyecto

```
Grupo8/
├── main.py
├── ai/
│   └── chat.py              # Lógica de IA conversacional
├── chat.py                  # Lógica del asistente de IA
├── config.py                # Configuración general
├── bd/
│   ├── sql.py               # Funciones para base de datos
│   ├── vector.py            # Funciones vectoriales para IA
│   └── data/
│       └── base_grupo8.db   # Base de datos SQLite, concimiento por tipo de cultivo.
├── requirements.txt         # Dependencias
├── Procfile                 # Despliegue en Heroku
├── runtime.txt              # Versión de Python para Heroku
├── startup.sh               # Script de inicio
```

## 🧪 Requisitos del Sistema

- Python 3.10+
- pip

### 📦 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/mbYTeGithub/Grupo8.git
   cd Grupo8
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el sistema:
   ```bash
   python main.py
   ```

## 🌐 Despliegue en Heroku (opcional)

Este proyecto está listo para desplegarse en [Heroku](https://heroku.com):

```bash
heroku create
git push heroku main
```

## 🧠 Base de Datos Incluida

- `base_nutricional_cultivos_top30.csv`: Información nutricional óptima para 30 cultivos alimentarios.
- `TIPO_SUELOS_GLOBALES.csv`: Tipologías de suelo a nivel global.
- `base_grupo8.db`: Base de datos consolidada para consultas automatizadas.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes abrir issues o hacer pull requests con mejoras, nuevos cultivos o nuevas funcionalidades para el asistente.

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 👥 Autoría

Proyecto desarrollado por el **Grupo 8** como parte de un trabajo académico con foco en soluciones de IA aplicadas al agro.

   Integrantes:
                **- Alejandro Fernández Escobar**
                **- Leonardo Rojas Castillo**
                **- Israel Barriga Inostroza**

