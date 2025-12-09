# NEO Monitoring - Como Executar

## 🎯 Opção 1: Executar do VS Code (SEM terminal visível)

### Primeira vez - Selecionar o Python correto:
1. Pressione `Ctrl+Shift+P` no VS Code
2. Digite: `Python: Select Interpreter`
3. Escolha: `.\env\Scripts\python.exe` (deve aparecer como "Python 3.x.x ('env': venv)")
4. **OU** clique na barra inferior direita onde mostra a versão do Python e selecione o interpretador do `env`

### Depois de selecionar o interpretador:
- Com `gui_main.py` aberto, pressione **F5** ou clique no botão ▶️ (Play)
- A aplicação abre normalmente, sem terminal!

---

## 🖱️ Opção 2: Duplo clique (SEM terminal visível)

### Usando VBS (RECOMENDADO - Mais limpo):
- Duplo clique em: **`NEO_Monitoring.vbs`**
- A aplicação abre sem mostrar terminal! ✨

### Usando BAT:
- Duplo clique em: **`run_gui.bat`**
- A aplicação abre e o terminal fecha sozinho

---

## ❓ Resolução de Problemas

### "ModuleNotFoundError: No module named 'pyodbc'"
**Causa:** VS Code está a usar Python do sistema em vez do ambiente virtual

**Solução:**
1. Pressione `Ctrl+Shift+P`
2. Digite: `Python: Select Interpreter`
3. Escolha: `.\env\Scripts\python.exe`
4. Reinicie o VS Code se necessário

### Como confirmar que está a usar o Python correto?
Olhe para a **barra inferior direita** do VS Code:
- ✅ Correto: `Python 3.x.x ('env': venv)`
- ❌ Errado: `Python 3.13.x` (sem 'env')

---

## 📁 Estrutura dos Arquivos de Execução

- **`NEO_Monitoring.vbs`** - Executa sem terminal (duplo clique) ⭐
- **`run_gui.bat`** - Executa via batch (duplo clique)
- **`.vscode/launch.json`** - Configuração para F5 no VS Code
- **`.vscode/settings.json`** - Define Python do ambiente virtual

---

## 💡 Dica Pro

Crie um atalho do `NEO_Monitoring.vbs` no ambiente de trabalho para acesso rápido! 🚀
