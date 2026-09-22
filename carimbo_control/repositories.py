"""Repositórios de dados da aplicação.

O modo Access é usado quando ACCESS_DB_PATH está configurado. Sem esse
caminho, o modo de demonstração mantém o programa executável localmente.
"""

from datetime import datetime
from pathlib import Path
import secrets

try:
    import pyodbc
except ImportError:  # pragma: no cover - mensagem clara no ambiente final
    pyodbc = None

from .config import Settings


class MemoryRepository:
    mode = "demonstração"

    def __init__(self):
        self.users = {
            "123456": {
                "chapa": "123456",
                "name": "João da Silva",
                "role": "supervisor",
                "department": "Produção",
                "password": "1234",
            },
            "654321": {
                "chapa": "654321",
                "name": "Maria Eduarda",
                "role": "operator",
                "department": "Qualidade",
                "password": "1234",
            },
        }
        self.occurrences = [
            {
                "protocol": "CAR-2025-0001",
                "collaborator": "João da Silva",
                "chapa": "123456",
                "type": "Carimbo perdido",
                "description": "Carimbo de inspeção não localizado no setor.",
                "status": "Em análise",
                "priority": "Alta",
                "created_at": "29/04/2025 09:15",
            },
            {
                "protocol": "CAR-2025-0002",
                "collaborator": "Maria Eduarda",
                "chapa": "654321",
                "type": "Troca de carimbo",
                "description": "Solicitação de substituição por desgaste.",
                "status": "Carimbo entregue",
                "priority": "Média",
                "created_at": "29/04/2025 08:30",
            },
            {
                "protocol": "CAR-2025-0003",
                "collaborator": "Carlos Alberto",
                "chapa": "789012",
                "type": "Funcionário novo",
                "description": "Cadastro de carimbo para novo colaborador.",
                "status": "Termo assinado",
                "priority": "Baixa",
                "created_at": "28/04/2025 16:45",
            },
            {
                "protocol": "CAR-2025-0004",
                "collaborator": "Ana Clara",
                "chapa": "345678",
                "type": "Carimbo danificado",
                "description": "Carimbo com texto ilegível.",
                "status": "Finalizado",
                "priority": "Média",
                "created_at": "28/04/2025 10:20",
            },
        ]

    def authenticate(self, chapa, password):
        user = self.users.get(chapa)
        if user and secrets.compare_digest(user["password"], password):
            return {key: value for key, value in user.items() if key != "password"}
        return None

    def list_occurrences(self, chapa=None):
        if chapa:
            return [item for item in self.occurrences if item["chapa"] == chapa]
        return list(self.occurrences)

    def create_occurrence(self, chapa, collaborator, occurrence_type, description, priority):
        item = {
            "protocol": f"CAR-{datetime.now():%Y}-{len(self.occurrences) + 1:04d}",
            "collaborator": collaborator,
            "chapa": chapa,
            "type": occurrence_type,
            "description": description,
            "status": "Em análise",
            "priority": priority,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self.occurrences.insert(0, item)
        return item

    def stats(self):
        items = self.occurrences
        return {
            "new": sum(item["status"] == "Em análise" for item in items),
            "pending": sum(
                item["status"] in {"Termo assinado", "Carimbo entregue"}
                for item in items
            ),
            "resolved": sum(item["status"] == "Finalizado" for item in items),
            "archived": 32,
        }


class AccessRepository:
    """Persistência Microsoft Access usando ODBC.

    Tabelas esperadas:
      Colaboradores(chapa, nome, senha, perfil, setor, ativo)
      Ocorrencias(protocolo, chapa, colaborador, tipo, descricao,
                  prioridade, status, criado_em)
    """

    mode = "Microsoft Access"

    def __init__(self, database_path, driver):
        self.database_path = database_path
        self.driver = driver

    def _connect(self):
        if pyodbc is None:
            raise RuntimeError("O pacote pyodbc não está instalado.")
        if not self.database_path:
            raise RuntimeError("ACCESS_DB_PATH não foi configurado.")
        if not Path(self.database_path).exists():
            raise RuntimeError(f"Arquivo Access não encontrado: {self.database_path}")
        connection_string = f"DRIVER={{{self.driver}}};DBQ={self.database_path};"
        return pyodbc.connect(connection_string)

    def authenticate(self, chapa, password):
        with self._connect() as connection:
            row = connection.cursor().execute(
                """
                SELECT chapa, nome, perfil, setor
                FROM Colaboradores
                WHERE chapa = ? AND senha = ? AND ativo = True
                """,
                chapa,
                password,
            ).fetchone()
        if not row:
            return None
        return {
            "chapa": str(row.chapa),
            "name": row.nome,
            "role": row.perfil or "operator",
            "department": row.setor or "Não informado",
        }

    def list_occurrences(self, chapa=None):
        query = """
            SELECT protocolo, colaborador, chapa, tipo, descricao,
                   status, prioridade, criado_em
            FROM Ocorrencias
        """
        params = []
        if chapa:
            query += " WHERE chapa = ?"
            params.append(chapa)
        query += " ORDER BY criado_em DESC"
        with self._connect() as connection:
            rows = connection.cursor().execute(query, *params).fetchall()
        return [
            {
                "protocol": row.protocolo,
                "collaborator": row.colaborador,
                "chapa": str(row.chapa),
                "type": row.tipo,
                "description": row.descricao or "",
                "status": row.status,
                "priority": row.prioridade,
                "created_at": (
                    row.criado_em.strftime("%d/%m/%Y %H:%M")
                    if hasattr(row.criado_em, "strftime")
                    else str(row.criado_em)
                ),
            }
            for row in rows
        ]

    def create_occurrence(self, chapa, collaborator, occurrence_type, description, priority):
        protocol = f"CAR-{datetime.now():%Y}-{datetime.now().timestamp():.0f}"[-8:]
        with self._connect() as connection:
            connection.cursor().execute(
                """
                INSERT INTO Ocorrencias
                  (protocolo, chapa, colaborador, tipo, descricao,
                   prioridade, status, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                protocol,
                chapa,
                collaborator,
                occurrence_type,
                description,
                priority,
                "Em análise",
                datetime.now(),
            )
            connection.commit()
        return {"protocol": protocol}

    def stats(self):
        items = self.list_occurrences()
        return {
            "new": sum(item["status"] == "Em análise" for item in items),
            "pending": sum(
                item["status"] in {"Termo assinado", "Carimbo entregue"}
                for item in items
            ),
            "resolved": sum(item["status"] == "Finalizado" for item in items),
            "archived": 0,
        }


def build_repository(settings=None):
    settings = settings or Settings.from_environment()
    if settings.access_configured:
        return AccessRepository(settings.access_db_path, settings.access_odbc_driver)
    if not settings.demo_allowed:
        raise RuntimeError(
            "ACCESS_DB_PATH não está configurado e o modo de demonstração foi desativado."
        )
    return MemoryRepository()