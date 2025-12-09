# src/ui.py
"""
Funções simples de interface de texto (UI) para a aplicação.
"""

def limpar_ecra():
    """Limpa o ecrã (de forma simples, portável)."""
    # Truque old-school: imprimir muitas quebras de linha
    print("\n" * 100)


def mostrar_ecran_inicial():
    limpar_ecra()
    print("==============================================")
    print("        NEO Monitoring - Sistema NEO          ")
    print("==============================================")
    print()
    print("Este programa permite:")
    print(" - Importar e gerir dados de asteroides NEO;")
    print(" - Consultar aproximações próximas e alertas;")
    print(" - Monitorizar estatísticas e eventos críticos.")
    print()
    print("Use o menu principal para navegar pelas opções.")
    print("==============================================")
    input("\nPrima ENTER para continuar para o menu...")


def mostrar_menu_principal() -> str:
    limpar_ecra()
    print("============== MENU PRINCIPAL ================")
    print("1) Aplicação de Inserção (processar ficheiros / inserir dados)")
    print("2) Aplicação de Alertas (listar e filtrar alertas)")
    print("3) Aplicação de Monitorização (estatísticas)")
    print("4) Consultas gerais (listar dados existentes)")
    print("5) Créditos")
    print("0) Sair")
    print("==============================================")
    opcao = input("Selecione uma opção: ").strip()
    return opcao


def mostrar_creditos():
    limpar_ecra()
    print("============== CRÉDITOS ======================")
    print("Trabalho realizado por:")
    print(" - Bernardete Coleho (aXXXX)")
    print(" - Carlos Farinha (a53481)")
    print()
    print("Unidade Curricular: Bases de Dados")
    print("Curso: Engenharia Informática")
    print("==============================================")
    input("\nPrima ENTER para regressar ao menu...")
