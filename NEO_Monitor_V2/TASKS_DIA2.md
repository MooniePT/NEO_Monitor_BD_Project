# NEO Monitor V2 - Tasks Detalhadas

## DIA 2 - Database Config & Dashboard

### 🔹 Task 1: DB Config Screen (45-60 min)

**Ficheiro:** `frontend/ui/db_config.py`

**Subtasks:**
1. [ ] Criar classe `DbConfigWindow(QWidget)`
2. [ ] Layout com QVBoxLayout
3. [ ] Campo "Servidor" - QLineEdit (default: `localhost\SQLEXPRESS`)
4. [ ] Campo "Base de Dados" - QLineEdit (default: `BD_PL2_09`)
5. [ ] Radio buttons autenticação:
   - [ ] QRadioButton "Windows"
   - [ ] QRadioButton "SQL Server"
6. [ ] Campos User/Password (QLineEdit):
   - [ ] Mostrar/esconder conforme radio button
   - [ ] Password com `setEchoMode(Password)`
7. [ ] Botão "Testar Conexão":
   - [ ] Chamar `backend.services.db_config.testar_conexao()`
   - [ ] QMessageBox.information se OK
   - [ ] QMessageBox.critical se ERRO
8. [ ] Botão "Conectar":
   - [ ] Chamar `ligar_bd()`
   - [ ] Emitir signal `connection_successful(conn)`
9. [ ] Guardar config em `config.json`:
   ```python
   import json
   config = {
       "server": "...",
       "database": "...",
       "auth_mode": "windows/sql"
   }
   with open("config.json", "w") as f:
       json.dump(config, f)
   ```

**Testar:**
- Windows auth deve conectar sem user/pass
- SQL auth deve pedir user/pass
- Conexão inválida deve mostrar erro claro

---

### 🔹 Task 2: Dashboard Screen (60-90 min)

**Ficheiro:** `frontend/ui/dashboard.py`

**Subtasks:**

#### Layout Principal
1. [ ] Criar classe `DashboardWindow(QWidget)`
2. [ ] Layout principal: QVBoxLayout
3. [ ] Título "Dashboard - Visão Geral"

#### KPIs (Cards)
4. [ ] Container QHBoxLayout para KPIs
5. [ ] Card 1 - Total NEOs:
   - [ ] QFrame com borda
   - [ ] QLabel "Total NEOs" (título)
   - [ ] QLabel "0" (valor grande, bold)
   - [ ] Query: `SELECT COUNT(*) FROM Asteroide WHERE flag_neo=1`
6. [ ] Card 2 - Total PHAs:
   - [ ] Similar ao Card 1
   - [ ] Cor diferente (vermelho/laranja)
   - [ ] Query: `SELECT COUNT(*) FROM Asteroide WHERE flag_pha=1`
7. [ ] Card 3 - Alertas Ativos:
   - [ ] Similar aos anteriores
   - [ ] Cor amarela
   - [ ] Query: `SELECT COUNT(*) FROM Alerta WHERE ativo=1`

#### Tabela de Asteroides
8. [ ] QLabel "Últimos Asteroides Detectados"
9. [ ] QTableWidget com colunas:
   - [ ] ID
   - [ ] Nome Completo
   - [ ] Diâmetro (km)
   - [ ] H (mag)
10. [ ] Preencher tabela:
    ```python
    from backend.services.consultas import fetch_ultimos_asteroides
    cols, rows = fetch_ultimos_asteroides(conn, limit=20)
    
    self.table.setRowCount(len(rows))
    for i, row in enumerate(rows):
        self.table.setItem(i, 0, QTableWidgetItem(str(row['id_asteroide'])))
        self.table.setItem(i, 1, QTableWidgetItem(row['nome_completo']))
        # etc.
    ```
11. [ ] Configurar tabela:
    - [ ] `setEditTriggers(QAbstractItemView.NoEditTriggers)` (read-only)
    - [ ] `setSelectionBehavior(QAbstractItemView.SelectRows)`
    - [ ] `horizontalHeader().setStretchLastSection(True)`

#### Atualização de Dados
12. [ ] Método `refresh_data(self, conn)`:
    - [ ] Re-executar queries dos KPIs
    - [ ] Atualizar labels
    - [ ] Re-popular tabela
13. [ ] Botão "Atualizar" que chama `refresh_data()`

**Testar:**
- KPIs devem mostrar números corretos da BD
- Tabela deve mostrar 20 asteroides mais recentes
- Botão Atualizar deve funcionar

---

### 🔹 Task 3: Integração Main Flow (30-45 min)

**Ficheiro:** `main.py`

**Subtasks:**
1. [ ] Import das novas windows:
   ```python
   from frontend.ui.login import LoginWindow
   from frontend.ui.db_config import DbConfigWindow
   from frontend.ui.dashboard import DashboardWindow
   ```

2. [ ] Atualizar `main()`:
   ```python
   def main():
       app = QApplication(sys.argv)
       
       # 1. Login
       login_window = LoginWindow()
       
       def on_login_success(username):
           login_window.hide()
           # 2. DB Config
           db_window = DbConfigWindow()
           
           def on_connection_success(conn):
               db_window.hide()
               # 3. Dashboard
               dashboard = DashboardWindow()
               dashboard.refresh_data(conn)
               dashboard.show()
           
           db_window.connection_successful.connect(on_connection_success)
           db_window.show()
       
       login_window.login_successful.connect(on_login_success)
       login_window.show()
       
       return app.exec()
   ```

3. [ ] Testar fluxo completo:
   - [ ] Login com admin/admin
   - [ ] DB Config com servidor correto
   - [ ] Dashboard abre e mostra dados

4. [ ] Tratamento de erros:
   - [ ] Se DB Config falhar, voltar a mostrar form
   - [ ] Botão "Logout" no Dashboard → volta ao Login

---

### 🔹 Task 4: Testes & Polish (15-30 min)

1. [ ] Testar com BD vazia (deve mostrar 0s nos KPIs)
2. [ ] Testar com BD populada
3. [ ] Testar conexão inválida (servidor errado)
4. [ ] Verificar cores e fontes consistentes
5. [ ] Screenshots para relatório

---

### 🔹 Task 5: Relatório LaTeX Dia 2 (20 min)

**Ficheiro:** `docs/reports/dia2_dbconfig_dashboard.tex`

1. [ ] Copiar template de `dia1_login.tex`
2. [ ] Documentar DB Config screen
3. [ ] Documentar Dashboard
4. [ ] Incluir screenshots
5. [ ] Código key snippets
6. [ ] Testes realizados

---

## Estimativa Total Dia 2

- DB Config: 45-60 min
- Dashboard: 60-90 min  
- Integração: 30-45 min
- Testes: 15-30 min
- Relatório: 20 min

**Total: 2.5 - 4 horas**

---

## Critérios de Aceitação Dia 2

✅ Login → DB Config → Dashboard funciona  
✅ KPIs mostram dados corretos da BD  
✅ Tabela mostra últimos 20 asteroides  
✅ Conexão inválida mostra erro claro  
✅ Zero crashes  
✅ Relatório LaTeX criado  

---

**IMPORTANTE:** Ler `ESTADO_ATUAL.md` antes de começar!
