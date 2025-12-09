# NEO Monitor BD Project - Monitorização de NEOs

Este projeto consiste numa aplicação gráfica (GUI) desenvolvida em Python para monitorização de "Near Earth Objects" (Objets Próximos da Terra), integrada com uma base de dados SQL Server.

## 📋 Descrição

A aplicação "NEO Monitoring" fornece um painel de controlo interativo que permite aos utilizadores visualizar e gerir dados sobre asteroides e outros corpos celestes monitorizados pela ESA/NASA. A aplicação suporta autenticação de administradores, configuração dinâmica da ligação à base de dados e importação de dados de ficheiros CSV e DAT (MPCORB).

## ✨ Funcionalidades

*   **Dashboard Interativo:** Interface gráfica moderna com fundo animado (estrelas e meteoros) desenvolvida em Tkinter.
*   **Autenticação:** Sistema de login seguro para administradores.
*   **Gestão de Base de Dados:**
    *   Configuração da ligação ao SQL Server através da interface.
    *   Suporte para Autenticação Windows e Autenticação SQL Server.
*   **Importação de Dados:**
    *   Importação automática de dados iniciais (`neo.csv`).
    *   Suporte para importação de ficheiros MPCORB (`MPCORB.DAT`).
    *   Importação de listas de risco da ESA (Risk List, Priority List, etc.).
*   **Visualização:** Tabelas para consulta de dados importados.
*   **Personalização:** Tema Claro/Escuro (Dark Mode).

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.x
*   **Interface Gráfica:** Tkinter (Standard Library)
*   **Base de Dados:** Microsoft SQL Server
*   **Librarias Python:**
    *   `pyodbc` (Conexão à base de dados)
    *   `Pillow` (Processamento de imagens)
    *   `tkinter` (GUI)

## 📁 Estrutura do Projeto

*   `NEO_Monitoring/src/`: Código fonte da aplicação Python.
    *   `gui_main.py`: Ponto de entrada da interface gráfica.
    *   `auth.py`: Lógica de autenticação.
    *   `db.py`: Gestão de ligações à base de dados.
    *   `services/`: Módulos para importação e consulta de dados.
*   `NEO_Monitoring/sql/`: Scripts SQL para criação e populamento da base de dados.
    *   `01_create_tables.sql`: Criação das tabelas.
    *   `02_create_views.sql`: Vistas para consultas.
    *   `03_create_triggers.sql`: Triggers de automação.
*   `NEO_Monitoring/assets/`: Recursos gráficos (imagens, ícones).
*   `NEO_Monitoring/docs/`: Documentação e ficheiros de dados exemplo.

## 🚀 Pré-requisitos

1.  **Python 3.10+** instalado.
2.  **Microsoft SQL Server** (Express ou Developer) instalado e a correr.
3.  **ODBC Driver for SQL Server** instalado (Geralmente incluído com o SQL Server ou SSMS).

## 📦 Instalação e Configuração

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/MooniePT/NEO_Monitor_BD_Project.git
    cd NEO_Monitor_BD_Project
    ```

2.  **Configurar Ambiente Python:**
    É recomendado usar um ambiente virtual (`venv`).
    ```bash
    # Windows
    python -m venv env
    .\env\Scripts\activate
    ```

3.  **Instalar Dependências:**
    ```bash
    pip install pyodbc Pillow
    ```

4.  **Configurar Base de Dados:**
    Execute os scripts SQL na pasta `NEO_Monitoring/sql` na seguinte ordem usando o SQL Server Management Studio (SSMS) ou Azure Data Studio:
    1.  `01_create_tables.sql`
    2.  `02_create_views.sql`
    3.  `03_create_triggers.sql`

## ▶️ Como Executar

Existem várias formas de iniciar a aplicação, localizadas na pasta `NEO_Monitoring`:

### Opção 1: Script VBS (Recomendado)
Execute o ficheiro **`NEO_Monitoring.vbs`**.
*   Abre a aplicação sem mostrar a janela da consola atrás.

### Opção 2: Script Batch
Execute o ficheiro **`run_gui.bat`**.

### Opção 3: Via Terminal/VS Code
```bash
cd NEO_Monitoring
python src/gui_main.py
```

## 🔑 Login Inicial

*   **Utilizador:** `Admin`
*   **Password:** `Admin123`
*(Consulte o ficheiro `users.json` para mais credenciais ou alterações)*

## 📄 Notas

*   Ao iniciar pela primeira vez, será solicitado que configure a ligação à base de dados (Servidor, BD).
*   Se a base de dados estiver vazia, a aplicação irá sugerir a importação do ficheiro `neo.csv` localizado em `docs`.

---
**Projeto desenvolvido no âmbito da unidade curricular de Bases de Dados.**
Grupo 09 @ UBI
