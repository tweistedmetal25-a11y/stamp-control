from .repositories import build_repository


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

    def is_supervisor(self):
        return bool(
            self.current_user
            and self.current_user.get("role") in {"supervisor", "admin"}
        )

    def occurrences(self, all_records=False):
        chapa = None if all_records or self.is_supervisor() else self.current_user["chapa"]
        return self.repository.list_occurrences(chapa)

    def create_occurrence(self, occurrence_type, description, priority, collaborator=None):
        if not self.current_user:
            raise RuntimeError("Faça login antes de registrar uma ocorrência.")
        return self.repository.create_occurrence(
            self.current_user["chapa"],
            collaborator or self.current_user["name"],
            occurrence_type,
            description,
            priority,
        )

    def stats(self):
        return self.repository.stats()