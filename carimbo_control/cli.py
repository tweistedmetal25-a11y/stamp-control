"""Interface local de terminal, sem Flask, servidor web ou API HTTP."""

from getpass import getpass
import os
import sys

from .services import StampControlService


PURPLE = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class TerminalApp:
    occurrence_types = (
        "Funcionário novo",
        "Carimbo perdido",
        "Carimbo danificado",
        "Troca de carimbo",
    )
    priorities = ("Baixa", "Média", "Alta")

    def __init__(self, service=None, input_fn=input, output_fn=print, password_fn=getpass):
        self.service = service or StampControlService()
        self.input = input_fn
        self.output = output_fn
        self.password = password_fn
        self.use_color = sys.stdout.isatty()

    def color(self, text, code):
        return f"{code}{text}{RESET}" if self.use_color else text

    def clear(self):
        if sys.stdout.isatty():
            os.system("clear")

    def pause(self):
        self.input("\nPressione Enter para continuar...")

    def header(self, title, subtitle=""):
        self.output("\n" + self.color("=" * 72, PURPLE))
        self.output(self.color(f"  CARIMBO+  |  {title}", BOLD))
        if subtitle:
            self.output(self.color(f"  {subtitle}", CYAN))
        self.output(self.color("=" * 72, PURPLE))

    def run(self):
        try:
            while True:
                if not self.login():
                    return
                if not self.main_menu():
                    return
        except (KeyboardInterrupt, EOFError):
            self.output("\n\nEncerrando o Carimbo+.")

    def login(self):
        attempts = 0
        while attempts < 3:
            self.clear()
            self.header("ACESSO SEGURO", "Sistema local de ocorrência de carimbo")
            self.output("\nAcesso restrito a colaboradores autorizados.")
            if self.service.mode == "demonstração":
                self.output(self.color("\nModo demonstração: chapa 123456 | senha 1234", YELLOW))
            chapa = self.input("\nChapa (ou 0 para sair): ").strip()
            if chapa == "0":
                return False
            senha = self.password("Senha: ")
            try:
                user = self.service.authenticate(chapa, senha)
            except Exception as exc:
                self.output(self.color(f"\nFalha ao consultar o banco: {exc}", RED))
                self.pause()
                return False
            if user:
                self.output(self.color(f"\nBem-vindo, {user['name'].split()[0]}!", GREEN))
                self.pause()
                return True
            attempts += 1
            self.output(self.color("\nChapa ou senha inválida.", RED))
            if attempts < 3:
                self.output(f"Tentativas restantes: {3 - attempts}")
                self.pause()
        self.output(self.color("\nAcesso bloqueado após três tentativas.", RED))
        return False

    def main_menu(self):
        while self.service.current_user:
            self.clear()
            user = self.service.current_user
            stats = self.service.stats()
            self.header("VISÃO GERAL", f"{user['name']} | Chapa {user['chapa']} | {self.service.mode}")
            self.output("\n" + self.color("RESUMO", BOLD))
            self.output(
                f"  Novas: {stats['new']}   Pendentes: {stats['pending']}   "
                f"Resolvidas: {stats['resolved']}"
            )
            self.output("\n" + self.color("MENU PRINCIPAL", BOLD))
            self.output("  1. Ocorrências recentes")
            self.output("  2. Nova ocorrência")
            self.output("  3. Minhas solicitações")
            if self.service.is_supervisor():
                self.output("  4. Central de notificações")
            self.output("  5. Como funciona")
            self.output("  0. Sair")
            choice = self.input("\nEscolha uma opção: ").strip()
            if choice == "1":
                self.show_occurrences(limit=8)
            elif choice == "2":
                self.new_occurrence()
            elif choice == "3":
                self.show_occurrences()
            elif choice == "4" and self.service.is_supervisor():
                self.show_notifications()
            elif choice == "5":
                self.show_how_it_works()
            elif choice == "0":
                self.service.logout()
                return True
            else:
                self.output(self.color("\nOpção inválida.", RED))
                self.pause()
        return True

    def show_occurrences(self, limit=None):
        self.clear()
        records = self.service.occurrences()
        self.header("SOLICITAÇÕES", f"{len(records)} registro(s)")
        if not records:
            self.output("\nNenhuma ocorrência encontrada.")
            self.pause()
            return
        for item in records[:limit]:
            self.output(
                f"\n{self.color(item['protocol'], BOLD)} | {item['status']} | "
                f"Prioridade {item['priority']}\n"
                f"  {item['type']} - {item['collaborator']} (chapa {item['chapa']})\n"
                f"  {item['created_at']} | {item['description']}"
            )
        self.pause()

    def choose(self, label, options):
        self.output(f"\n{label}")
        for index, option in enumerate(options, 1):
            self.output(f"  {index}. {option}")
        while True:
            value = self.input("Selecione: ").strip()
            if value.isdigit() and 1 <= int(value) <= len(options):
                return options[int(value) - 1]
            self.output(self.color("Escolha inválida.", RED))

    def new_occurrence(self):
        self.clear()
        self.header("NOVA OCORRÊNCIA", "Registro rastreável")
        occurrence_type = self.choose("Tipo de ocorrência", self.occurrence_types)
        priority = self.choose("Prioridade", self.priorities)
        collaborator = self.input(
            f"Colaborador [{self.service.current_user['name']}]: "
        ).strip() or self.service.current_user["name"]
        description = self.input("Descrição: ").strip()
        if not description:
            self.output(self.color("\nA descrição é obrigatória.", RED))
            self.pause()
            return
        try:
            created = self.service.create_occurrence(
                occurrence_type, description, priority, collaborator
            )
            self.output(
                self.color(
                    f"\nOcorrência {created['protocol']} registrada com sucesso.",
                    GREEN,
                )
            )
        except Exception as exc:
            self.output(self.color(f"\nNão foi possível registrar: {exc}", RED))
        self.pause()

    def show_notifications(self):
        self.clear()
        records = self.service.occurrences(all_records=True)
        stats = self.service.stats()
        self.header("CENTRAL DE NOTIFICAÇÕES", "Área restrita para responsáveis")
        self.output(
            f"\nNovas: {stats['new']} | Pendentes: {stats['pending']} | "
            f"Resolvidas: {stats['resolved']} | Arquivadas: {stats['archived']}"
        )
        for item in records[:12]:
            self.output(
                f"\n{item['protocol']} | {item['priority']} | {item['status']}\n"
                f"  {item['collaborator']} - {item['type']} - {item['created_at']}"
            )
        self.pause()

    def show_how_it_works(self):
        self.clear()
        self.header("COMO FUNCIONA")
        self.output(
            "\n1. Registre: abra uma ocorrência para carimbo novo, perdido, "
            "danificado ou troca."
            "\n2. Acompanhe: consulte o protocolo e o status no menu de "
            "solicitações."
            "\n3. Conclua: o responsável atualiza o andamento e preserva o "
            "histórico para auditoria."
        )
        self.pause()


def run():
    TerminalApp().run()