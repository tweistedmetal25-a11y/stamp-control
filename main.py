import os
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for

try:
    import pyodbc
except ImportError:  # pragma: no cover - available after dependency setup
    pyodbc = None


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
app.config["ACCESS_DB_PATH"] = os.getenv("ACCESS_DB_PATH", "").strip()
app.config["ACCESS_ODBC_DRIVER"] = os.getenv(
    "ACCESS_ODBC_DRIVER", "Microsoft Access Driver (*.mdb, *.accdb)"
)


class MemoryRepository:
    """Local preview repository used when ACCESS_DB_PATH is not configured."""

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

    @property
    def mode(self):
        return "demonstração"

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
        next_number = len(self.occurrences) + 1
        item = {
            "protocol": f"CAR-2025-{next_number:04d}",
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
            "pending": sum(item["status"] in {"Termo assinado", "Carimbo entregue"} for item in items),
            "resolved": sum(item["status"] == "Finalizado" for item in items),
            "archived": 32,
        }


class AccessRepository:
    """Microsoft Access repository.

    Expected tables:
      Colaboradores(chapa, nome, senha, perfil, setor, ativo)
      Ocorrencias(protocolo, chapa, colaborador, tipo, descricao, prioridade, status, criado_em)
    """

    def __init__(self, database_path, driver):
        self.database_path = database_path
        self.driver = driver

    @property
    def mode(self):
        return "Microsoft Access"

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
            SELECT protocolo, colaborador, chapa, tipo, descricao, status,
                   prioridade, criado_em
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
                "created_at": row.criado_em.strftime("%d/%m/%Y %H:%M")
                if hasattr(row.criado_em, "strftime")
                else str(row.criado_em),
            }
            for row in rows
        ]

    def create_occurrence(self, chapa, collaborator, occurrence_type, description, priority):
        protocol = f"CAR-{datetime.now():%Y}-{datetime.now().timestamp():.0f}"[-8:]
        with self._connect() as connection:
            connection.cursor().execute(
                """
                INSERT INTO Ocorrencias
                  (protocolo, chapa, colaborador, tipo, descricao, prioridade, status, criado_em)
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
            "pending": sum(item["status"] in {"Termo assinado", "Carimbo entregue"} for item in items),
            "resolved": sum(item["status"] == "Finalizado" for item in items),
            "archived": 0,
        }


repository = (
    AccessRepository(app.config["ACCESS_DB_PATH"], app.config["ACCESS_ODBC_DRIVER"])
    if app.config["ACCESS_DB_PATH"]
    else MemoryRepository()
)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            flash("Entre com sua chapa e senha para continuar.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def supervisor_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session["user"].get("role") not in {"supervisor", "admin"}:
            flash("Esta área é exclusiva para responsáveis autorizados.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_layout_data():
    return {
        "app_name": "Carimbo+",
        "repository_mode": repository.mode,
        "current_year": datetime.now().year,
    }


@app.route("/", methods=["GET"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.get("/favicon.ico")
def favicon():
    return Response(status=204)


@app.post("/login")
def authenticate():
    chapa = request.form.get("chapa", "").strip()
    password = request.form.get("password", "")
    if not chapa or not password:
        flash("Informe sua chapa e senha.", "error")
        return redirect(url_for("login"))
    try:
        user = repository.authenticate(chapa, password)
    except Exception:
        app.logger.exception("Falha ao consultar o Microsoft Access")
        flash("Não foi possível consultar o banco de acesso. Verifique a configuração.", "error")
        return redirect(url_for("login"))
    if not user:
        flash("Chapa ou senha inválida.", "error")
        return redirect(url_for("login"))
    session["user"] = user
    session.permanent = True
    flash(f"Bem-vindo, {user['name'].split()[0]}!", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        items = repository.list_occurrences()
        stats = repository.stats()
    except Exception:
        app.logger.exception("Falha ao carregar ocorrências")
        items, stats = [], {"new": 0, "pending": 0, "resolved": 0, "archived": 0}
        flash("Não foi possível carregar as ocorrências do Access.", "error")
    return render_template("dashboard.html", occurrences=items[:4], stats=stats)


@app.route("/ocorrencias/nova", methods=["GET", "POST"])
@login_required
def new_occurrence():
    if request.method == "POST":
        occurrence_type = request.form.get("type", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Média").strip()
        collaborator = request.form.get("collaborator", session["user"]["name"]).strip()
        if not occurrence_type or not description:
            flash("Selecione o tipo e descreva a ocorrência.", "error")
            return render_template("new_occurrence.html")
        try:
            created = repository.create_occurrence(
                session["user"]["chapa"],
                collaborator,
                occurrence_type,
                description,
                priority,
            )
            flash(f"Ocorrência {created['protocol']} registrada com sucesso.", "success")
            return redirect(url_for("requests"))
        except Exception:
            app.logger.exception("Falha ao registrar ocorrência")
            flash("Não foi possível registrar a ocorrência no Access.", "error")
    return render_template("new_occurrence.html")


@app.route("/solicitacoes")
@login_required
def requests():
    try:
        occurrences = repository.list_occurrences(
            None if session["user"].get("role") in {"supervisor", "admin"} else session["user"]["chapa"]
        )
    except Exception:
        app.logger.exception("Falha ao carregar solicitações")
        occurrences = []
        flash("Não foi possível carregar suas solicitações.", "error")
    return render_template("requests.html", occurrences=occurrences)


@app.route("/notificacoes")
@supervisor_required
def notifications():
    try:
        occurrences = repository.list_occurrences()
        stats = repository.stats()
    except Exception:
        occurrences, stats = [], {"new": 0, "pending": 0, "resolved": 0, "archived": 0}
        flash("Não foi possível carregar a central de notificações.", "error")
    return render_template("notifications.html", occurrences=occurrences, stats=stats)


@app.get("/como-funciona")
@login_required
def how_it_works():
    return render_template("how_it_works.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)