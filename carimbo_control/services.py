from .repositories import build_repository


PRIORITIES = ("Baixa", "Média", "Alta")
STATUSES = ("Em andamento", "Concluído")
DEFAULT_PRIORITY = "Média"


class StampControlService:
    def __init__(self, repository=None):
        self.repository = repository or build_repository()
        self.current_user = None

    @property
    def mode(self):
        return self.repository.mode

    def authenticate(self, chapa, password):
        user = self.repository.authenticate(chapa.strip(), password)
        if user:
            self.current_user = user
        return user

    def logout(self):
        self.current_user = None

    def is_admin(self):
        role = str((self.current_user or {}).get("role", "")).strip().casefold()
        return bool(
            self.current_user
            and role in {
                "admin",
                "administrator",
                "administrador",
                "supervisor",
                "responsavel",
                "responsável",
            }
        )

    def is_supervisor(self):
        """Compatibilidade com telas e perfis antigos de responsável."""
        return self.is_admin()

    def occurrences(self, all_records=False):
        if not self.current_user:
            raise RuntimeError("Faça login antes de consultar as solicitações.")
        chapa = None if self.is_admin() else self.current_user["chapa"]
        return self.repository.list_occurrences(chapa)

    def update_occurrence(self, protocol, priority, status):
        if not self.current_user:
            raise RuntimeError("Faça login antes de alterar uma solicitação.")
        if not self.is_admin():
            raise PermissionError("Somente administradores podem alterar solicitações.")
        if priority not in PRIORITIES:
            raise ValueError("Prioridade inválida.")
        if status not in STATUSES:
            raise ValueError("Status inválido.")
        if not self.repository.update_occurrence(protocol, priority, status):
            raise LookupError("Solicitação não encontrada.")
        return True

    def create_occurrence(self, occurrence_type, description, priority, collaborator=None):
        if not self.current_user:
            raise RuntimeError("Faça login antes de registrar uma ocorrência.")
        if self.is_admin():
            if priority not in PRIORITIES:
                raise ValueError("Prioridade inválida.")
        else:
            priority = DEFAULT_PRIORITY
        return self.repository.create_occurrence(
            self.current_user["chapa"],
            collaborator or self.current_user["name"],
            occurrence_type,
            description,
            priority,
        )

    def stats(self):
        if not self.current_user:
            raise RuntimeError("Faça login antes de consultar os indicadores.")
        if self.is_admin():
            return self.repository.stats()
        records = self.repository.list_occurrences(self.current_user["chapa"])
        statuses = [item["status"] for item in records]
        return {
            "new": sum(status in {"Em análise", "Em andamento"} for status in statuses),
            "pending": sum(
                status in {"Termo assinado", "Carimbo entregue"}
                for status in statuses
            ),
            "resolved": sum(status in {"Finalizado", "Concluído"} for status in statuses),
            "archived": 0,
        }