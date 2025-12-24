# NEO Monitor V2 - Plano de Desenvolvimento Completo

**Projeto:** Reescrita completa do frontend NEO Monitor  
**Tecnologia:** PyQt6  
**Prazo:** 24 Dez → 31 Dez 2024 (7 dias)  
**Status Atual:** DIA 1 COMPLETO ✅

---

## Objetivo Geral

Criar uma aplicação desktop moderna, estável e profissional para monitorização de asteroides NEO, mantendo o backend SQL Server existente e reescrevendo todo o frontend em PyQt6.

---

## Timeline Completa (7 Dias)

### ✅ **DIA 1 (24 Dez) - COMPLETO**
- [x] Decisão e planeamento
- [x] Criar estrutura projeto NEO_Monitor_V2
- [x] Copiar backend (SQL scripts, CSV, serviços Python)
- [x] Instalar PyQt6
- [x] **Login Screen funcional e testado**
- [x] Relatório LaTeX Dia 1

**Resultado:** Login perfeito, sem bugs, profissional.

---

### 🔄 **DIA 2 (25 Dez) - PRÓXIMO**

#### Tela de Configuração BD
- [ ] Criar `frontend/ui/db_config.py`
- [ ] Form com campos:
  - Servidor (ex: `localhost\SQLEXPRESS`)
  - Base de Dados (ex: `BD_PL2_09`)
  - Tipo Auth: Radio buttons (Windows / SQL Server)
  - User/Pass (mostrar/esconder conforme tipo auth)
- [ ] Botão "Testar Conexão"
  - Usar `backend/services/db_config.py` existente
  - Mostrar mensagem de sucesso/erro
- [ ] Botão "Conectar" → Abre Dashboard
- [ ] Guardar configuração em JSON

#### Dashboard Base
- [ ] Criar `frontend/ui/dashboard.py`
- [ ] 3 KPIs no topo (cards):
  - Total NEOs (query: `SELECT COUNT(*) FROM Asteroide WHERE flag_neo=1`)
  - Total PHAs (query: `SELECT COUNT(*) FROM Asteroide WHERE flag_pha=1`)
  - Alertas Ativos (query: `SELECT COUNT(*) FROM Alerta WHERE ativo=1`)
- [ ] Tabela: Últimos 20 asteroides
  - Usar `backend/services/consultas.fetch_ultimos_asteroides()`
  - Colunas: ID, Nome, Diâmetro, H_mag
- [ ] Layout QVBoxLayout limpo

#### Integração
- [ ] Atualizar `main.py` para fluxo: Login → DBConfig → Dashboard
- [ ] Signals entre telas (PyQt signals)
- [ ] Testes completos

**Estimativa:** 2-2.5 horas

---

### 📅 **DIA 3 (26 Dez)**

#### Pesquisa Completa
- [ ] Criar `frontend/ui/search.py`
- [ ] Filtros:
  - Campo texto: Nome/Designação
  - Dropdown: Tipo (Todos/NEO/PHA)
  - Dropdown: Ordenação (Nome, Tamanho, Perigo)
- [ ] Tabela de resultados (QTableWidget)
- [ ] Paginação:
  - Botões "Anterior" / "Próxima"
  - Label "Página X de Y (Z total)"
  - 50 registos por página
- [ ] Usar `backend/services/consultas.fetch_filtered_asteroids()`

**Estimativa:** 2 horas

---

### 📅 **DIA 4 (27 Dez)**

#### Inserção Manual
- [ ] Criar `frontend/ui/insert.py`
- [ ] Form com campos principais:
  - Nome completo
  - Designação
  - Diâmetro (km)
  - H_mag
  - MOID
  - Flags: NEO, PHA (checkboxes)
- [ ] Validação de campos
- [ ] Botão "Inserir" → Chama `backend/services/insercao.py`
- [ ] Mensagem de sucesso/erro

#### Importação CSV
- [ ] Botão "Importar CSV"
- [ ] File dialog para selecionar ficheiro
- [ ] Loading bar durante importação
- [ ] Usar lógica existente de `insercao.py`

**Estimativa:** 2 horas

---

### 📅 **DIA 5 (28 Dez)**

#### Alertas
- [ ] Criar `frontend/ui/alerts.py`
- [ ] Tabela de alertas:
  - ID, Asteroide, Data, Distância, Tipo, Ativo
- [ ] Cores indicadoras:
  - Vermelho: Alta prioridade
  - Amarelo: Média
  - Verde: Baixa
- [ ] Filtro: Mostrar só ativos / Todos
- [ ] Query: `SELECT * FROM Alerta ORDER BY data_alerta DESC`

#### Monitorização
- [ ] Criar `frontend/ui/monitoring.py`
- [ ] 3 tabs:
  1. **Ranking PHAs** (mais perigosos)
  2. **Centros de Observação** (estatísticas)
  3. **Aproximações Críticas** (próximas da Terra)
- [ ] Usar views/queries SQL existentes

**Estimativa:** 2-3 horas

---

### 📅 **DIA 6 (29 Dez)**

#### Polish UI
- [ ] Revisão geral de todas as telas
- [ ] Consistência de cores e fontes
- [ ] Ícones (se necessário)
- [ ] Mensagens de erro user-friendly
- [ ] Tooltips em botões

#### Testes de Integração
- [ ] Teste completo: Login → DB → Dashboard → Pesquisa → Inserção → Alertas
- [ ] Teste de erros (BD offline, credenciais erradas, etc.)
- [ ] Performance com muitos dados
- [ ] Fix de bugs encontrados

**Estimativa:** 3-4 horas

---

### 📅 **DIA 7 (30 Dez) - RESERVA**

#### Testes Finais
- [ ] User testing
- [ ] Correção de bugs críticos
- [ ] Documentação final

#### Documentação
- [ ] README.md completo
- [ ] Instruções de instalação
- [ ] Manual de uso
- [ ] Relatório LaTeX final consolidado

**Estimativa:** Buffer para imprevistos

---

## Tecnologias Backend (Mantidas)

- SQL Server (local ou remoto)
- Scripts SQL:
  - `00_reset_database.sql`
  - `01_create_schema.sql`
  - `02_views.sql`
  - `03_triggers.sql`
  - `04_seed_data.sql`
  - `99_verify_import.sql`
- Serviços Python:
  - `db_config.py` - Conexão BD
  - `consultas.py` - Queries
  - `insercao.py` - Insert/Import
  - `auth.py` - Autenticação

---

## Funcionalidades MVP (Mínimas)

1. ✅ **Login** - Autenticação admin
2. 🔄 **DB Config** - Configurar conexão
3. 🔄 **Dashboard** - Visão geral (KPIs + tabela)
4. 📅 **Pesquisa** - Filtrar e listar asteroides
5. 📅 **Inserção** - Adicionar asteroides (manual + CSV)
6. 📅 **Alertas** - Listar alertas com cores
7. 📅 **Monitorização** - Rankings e estatísticas

---

## Critérios de Sucesso

- ✅ Zero crashes
- ✅ UI profissional e legível
- ✅ Todas as funcionalidades funcionais
- ✅ Código limpo e organizado
- ✅ Documentação completa
- ✅ Entregue até 31 Dezembro

---

## Arquitetura Técnica

```
PyQt6 Frontend (NEO_Monitor_V2)
    ↓ (signals/slots)
Backend Services (Python)
    ↓ (pyodbc)
SQL Server Database
```

---

## Riscos & Mitigações

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Não terminar a tempo | BAIXA | Scope reduzido dia 7 |
| Bugs de última hora | MÉDIA | Dia 6 dedicado a testes |
| Problemas SQL Server | BAIXA | Backend já funciona |
| PyQt6 complexidades | BAIXA | Arquitetura simples |

---

## Contactos & Recursos

- **Repo:** `c:\Users\Carlos\Documents\GitHub\NEO_Monitor_BD_Project\NEO_Monitor_V2`
- **Documentação:** `docs/reports/`
- **Credenciais padrão:** admin/admin

---

**Última atualização:** 24 Dez 2024, 02:40  
**Status:** DIA 1 COMPLETO - Pronto para DIA 2
