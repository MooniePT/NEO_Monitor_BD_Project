# src/main.py
"""
Ponto de entrada da aplicação NEO Monitoring.
Fluxo:
  1) Login de administrador
  2) Ligação à base de dados
  3) Ecrã inicial
  4) Menu principal (loop)
"""

from auth import pedir_login_admin
from db import pedir_e_ligar_bd, LigacaoBDFalhada
from ui import mostrar_ecran_inicial, mostrar_menu_principal, mostrar_creditos


def tratar_opcao_menu(opcao: str, ligacao_bd):
    """
    Trata uma opção do menu principal.
    Por agora, apenas placeholders; vamos completar mais tarde.
    """
    if opcao == "1":
        print("\n[Inserção] Aqui vamos processar ficheiros / inserir dados...")
        # TODO: chamar funções de services para inserir dados
        input("\nPrima ENTER para voltar ao menu...")

    elif opcao == "2":
        print("\n[Alertas] Aqui vamos listar e filtrar alertas...")
        # TODO: chamar funções de services para alertas
        input("\nPrima ENTER para voltar ao menu...")

    elif opcao == "3":
        print("\n[Monitorização] Aqui vamos mostrar estatísticas...")
        # TODO: chamar funções de services para estatísticas
        input("\nPrima ENTER para voltar ao menu...")

    elif opcao == "4":
        print("\n[Consultas] Aqui vamos listar dados (ex: asteroides, observações)...")
        # TODO: chamar funções de services para consultas gerais
        input("\nPrima ENTER para voltar ao menu...")

    elif opcao == "5":
        mostrar_creditos()

    else:
        print("\n[ERRO] Opção inválida.")
        input("\nPrima ENTER para voltar ao menu...")


def main():
    # 1) Login de administrador
    try:
        _ = pedir_login_admin()
    except PermissionError as exc:
        print(f"\n[ERRO] {exc}")
        print("A aplicação será terminada.")
        return

    # 2) Ligação à base de dados
    try:
        ligacao = pedir_e_ligar_bd()
    except LigacaoBDFalhada as exc:
        print(f"\n[ERRO FATAL] {exc}")
        print("Não foi possível estabelecer ligação à base de dados. A aplicação será terminada.")
        return

    # 3) Ecrã inicial
    mostrar_ecran_inicial()

    # 4) Loop do menu principal
    sair = False
    while not sair:
        opcao = mostrar_menu_principal()

        if opcao == "0":
            confirmar = input("Tem a certeza que deseja sair? (S/N): ").strip().upper()
            if confirmar == "S":
                sair = True
            continue

        tratar_opcao_menu(opcao, ligacao)

    # 5) Fechar ligação e terminar
    try:
        ligacao.close()
    except Exception:
        pass

    print("\nAplicação terminada. Obrigado por utilizar o NEO Monitoring.\n")


if __name__ == "__main__":
    main()
