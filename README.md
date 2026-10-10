# NEO Monitor – Near-Earth Object Monitoring Database

A Python desktop application backed by a Microsoft SQL Server database for monitoring Near-Earth Objects (asteroids and comets). It imports real orbital data from the Minor Planet Center (MPCORB, ~966,000 objects) and ESA risk lists, then lets users browse, query and manage it through a Tkinter GUI.

> **Academic group project** – Databases course, University of Beira Interior (UBI), Group 09.
> Team: Carlos Farinha, Bernardete Coelho.

## Screenshots

<!-- Add screenshots to docs/screenshots/ and uncomment:
![Login](docs/screenshots/login.png)
![Dashboard](docs/screenshots/dashboard.png)
![Query results](docs/screenshots/queries.png)
![ER diagram](Documentos%20para%20relatorio/Relatorio/Diagrama.png)
-->

## Features

- **Relational database design**: 19 tables, 14 views and 4 triggers (asteroids, orbital solutions, close approaches, alerts, observations, observatories, equipment, ESA lists)
- **Bulk data import** from `MPCORB.DAT` and CSV files, run in a background thread to keep the UI responsive
- **ESA risk list integration** (risk list, special risk list, past impactors, upcoming close approaches)
- **Query screens** for NEOs, potentially hazardous asteroids (PHAs), alerts and statistics
- **Database connection settings** in the GUI, with Windows or SQL Server authentication
- **Admin login and user management**
- Light/dark theme and an animated starfield background

## Tech Stack

- Python 3.10+ with Tkinter
- Microsoft SQL Server (T-SQL: tables, views, triggers)
- pyodbc, Pillow
- dbdiagram.io / ERDPlus for data modelling, LaTeX for the technical report

## Getting Started

**Requirements:** Python 3.10+, SQL Server (Express or Developer), ODBC Driver for SQL Server (Windows).

1. **Clone and set up the environment**
   ```bash
   git clone https://github.com/MooniePT/NEO_Monitor_BD_Project.git
   cd NEO_Monitor_BD_Project/NEO_Monitoring
   python -m venv env
   env\Scripts\activate
   pip install pyodbc Pillow
   ```
2. **Create the database.** Run the scripts in `NEO_Monitoring/sql/` in order (SSMS or Azure Data Studio): `01_create_tables.sql`, `02_create_views.sql`, `03_create_triggers.sql` and, optionally, `04_seed_data.sql`.
3. **Run the app** from the `NEO_Monitoring` folder:
   ```bash
   python src/gui_main.py
   ```
   On Windows you can also double-click `NEO_Monitoring.vbs` or `run_gui.bat`.
4. On first launch, enter the SQL Server instance and database name. A local `users.json` is created with a demo admin account (`admin` / `admin123`). Change it in the user-management screen.

`config.json` and `users.json` are created locally and are intentionally not tracked by Git.

## Project Structure

```
NEO_Monitor_BD_Project/
├── NEO_Monitoring/
│   ├── src/
│   │   ├── gui_main.py          # GUI entry point
│   │   ├── main.py / ui.py      # Console version
│   │   ├── auth.py              # Admin login and user management
│   │   ├── db.py                # SQL Server connection (pyodbc)
│   │   ├── services/            # Data import (MPCORB, CSV, ESA) and queries
│   │   └── tools/               # Maintenance scripts
│   ├── sql/                     # Schema, views, triggers, seed and checks
│   ├── docs/                    # Sample ESA CSV data + MPCORB converter
│   └── assets/                  # Logos
└── Documentos para relatorio/   # ER diagrams, SQL drafts and LaTeX report (Portuguese)
```

## What I Learned

- Modelling a real-world domain into a normalised relational schema (ER diagram → T-SQL)
- Writing views and triggers to enforce rules and simplify queries
- Importing and validating large datasets (~1M rows) efficiently from Python
- Connecting a Python GUI to SQL Server and handling connection and authentication errors
