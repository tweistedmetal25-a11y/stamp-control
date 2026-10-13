"""Interface gráfica nativa Qt para o sistema Carimbo+."""

import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .services import (
    DEFAULT_PRIORITY,
    OCCURRENCE_TYPES,
    OPERATOR_OCCURRENCE_TYPES,
    PRIORITIES,
    STATUSES,
    StampControlService,
)


PURPLE = "#4724ad"
PURPLE_DARK = "#1e105e"
INK = "#211b43"
MUTED = "#777488"
LINE = "#e8e5f0"
SURFACE = "#f7f6fb"


APP_STYLESHEET = """
QWidget {
    color: #211b43;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
}
QLabel { background: transparent; }
QMainWindow, QWidget#appRoot { background: #f7f6fb; }
QLabel#eyebrow { color: #8774ca; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
QLabel#pageTitle { color: #211b43; font-size: 26px; font-weight: 750; }
QLabel#sectionTitle { color: #272044; font-size: 16px; font-weight: 700; }
QLabel#muted { color: #777488; }
QFrame#sidebar { background: #1c1058; border: none; }
QLabel#brandTitle { color: white; font-size: 16px; font-weight: 800; }
QLabel#brandSubtitle { color: #c4b9ed; font-size: 9px; }
QPushButton#navButton {
    color: #eeeaff; background: transparent; border: none; border-radius: 8px;
    text-align: left; padding: 12px 13px; font-size: 12px; font-weight: 600;
}
QPushButton#navButton:hover { background: #302075; }
QPushButton#navButton:checked { background: #5430bf; color: white; }
QPushButton#logoutButton {
    background: #302075; color: white; border: none; border-radius: 8px;
    padding: 11px; text-align: left; font-weight: 600;
}
QFrame#topbar { background: white; border-bottom: 1px solid #e8e5f0; }
QLabel#topbarTitle { color: #302262; font-size: 14px; font-weight: 800; }
QLabel#avatar {
    background: #4724ad; color: white; border-radius: 18px; min-width: 36px;
    max-width: 36px; min-height: 36px; max-height: 36px; font-weight: 800;
}
QFrame#card, QFrame#formCard, QFrame#tableCard {
    background: white; border: 1px solid #e8e5f0; border-radius: 11px;
}
QFrame#hero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #281075, stop:1 #4d25a8);
    border: none; border-radius: 12px;
}
QLabel#heroTitle { color: white; font-size: 24px; font-weight: 800; }
QLabel#heroBody { color: #e1d9ff; font-size: 12px; }
QLabel#heroAccent { color: #7be09b; }
QLabel#stampArt {
    color: #e5dcff; background: rgba(255,255,255,0.11); border: 1px solid #7555d2;
    border-radius: 24px; font-size: 40px; font-weight: 800;
}
QFrame#quickCard { background: white; border: 1px solid #e8e5f0; border-radius: 10px; }
QPushButton#quickButton {
    background: transparent; border: none; text-align: left; padding: 0;
}
QPushButton#primaryButton {
    color: white; background: #4b27b3; border: none; border-radius: 7px;
    min-height: 39px; padding: 0 16px; font-weight: 700;
}
QPushButton#primaryButton:hover { background: #613bd0; }
QPushButton#secondaryButton {
    color: #4724ad; background: white; border: 1px solid #dcd7e9;
    border-radius: 7px; min-height: 36px; padding: 0 13px; font-weight: 700;
}
QPushButton#secondaryButton:hover { background: #f5f2ff; }
QLineEdit, QComboBox, QTextEdit {
    color: #211b43; background: white; border: 1px solid #e0dce9;
    border-radius: 6px; padding: 9px 11px; selection-background-color: #7652d5;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 1px solid #7652d5; }
QLabel#fieldLabel { color: #45405f; font-size: 10px; font-weight: 800; }
QTableWidget {
    background: white; border: none; gridline-color: #f0eef5;
    selection-background-color: #f1edff; selection-color: #211b43;
}
QHeaderView::section {
    background: #fbfaff; color: #6f6b85; border: none;
    border-bottom: 1px solid #ece9f2; padding: 10px 8px; font-size: 10px; font-weight: 800;
}
QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0eef5; }
QScrollArea { border: none; background: transparent; }
QLabel#noticeTitle { color: white; font-size: 18px; font-weight: 800; }
QLabel#noticeBody { color: #d4ccef; font-size: 11px; }
QLabel#metricValue { color: #211b43; font-size: 23px; font-weight: 800; }
QLabel#metricCaption { color: #777488; font-size: 10px; }
QMessageBox { background: white; }
"""


class BrandMark(QLabel):
    def __init__(self, light=False, parent=None):
        super().__init__("✦", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(42, 42)
        self.setStyleSheet(
            f"color:{'white' if light else PURPLE}; border:2px solid "
            f"{'white' if light else '#6b4be7'}; border-radius:21px; font-size:21px;"
        )


def eyebrow(text):
    label = QLabel(text.upper())
    label.setObjectName("eyebrow")
    return label


def page_title(title, subtitle=None):
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 8)
    layout.setSpacing(4)
    layout.addWidget(eyebrow("Carimbo+  /  Controle"))
    title_label = QLabel(title)
    title_label.setObjectName("pageTitle")
    layout.addWidget(title_label)
    if subtitle:
        sub = QLabel(subtitle)
        sub.setObjectName("muted")
        layout.addWidget(sub)
    return container


def make_button(text, primary=True):
    button = QPushButton(text)
    button.setObjectName("primaryButton" if primary else "secondaryButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def make_table(headers, rows, min_height=210):
    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setMinimumHeight(min_height)
    table.setAlternatingRowColors(False)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setToolTip(str(value))
            table.setItem(row_index, col_index, item)
    table.horizontalHeader().setStretchLastSection(True)
    table.resizeColumnsToContents()
    table.horizontalHeader().setMinimumSectionSize(84)
    return table


class LoginWindow(QWidget):
    authenticated = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setWindowTitle("Carimbo+ · Acesso seguro")
        self.setMinimumSize(880, 610)
        self.resize(1160, 730)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        promo = QFrame()
        promo.setObjectName("loginPromo")
        promo.setStyleSheet(
            "QFrame#loginPromo{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #2d107f,stop:0.65 #39198d,stop:1 #1f0c69);}"
        )
        promo_layout = QVBoxLayout(promo)
        promo_layout.setContentsMargins(58, 50, 48, 35)
        brand_row = QHBoxLayout()
        brand_row.addWidget(BrandMark(light=True))
        brand_text = QVBoxLayout()
        company = QLabel("KROMBERG\n& SCHUBERT")
        company.setStyleSheet("color:white;font-size:18px;font-weight:800;")
        brand_text.addWidget(company)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        promo_layout.addLayout(brand_row)
        promo_layout.addSpacing(55)
        promo_layout.addWidget(QLabel("SISTEMA DE", styleSheet="color:#eee8ff;font-size:14px;font-weight:700;"))
        promo_title = QLabel("OCORRÊNCIA\nDE CARIMBO")
        promo_title.setStyleSheet("color:white;font-size:38px;font-weight:900;")
        promo_layout.addWidget(promo_title)
        promo_layout.addSpacing(18)
        desc = QLabel("Registro e controle de perda, dano, troca e entrega de carimbos.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#ded7ff;font-size:13px;")
        promo_layout.addWidget(desc)
        promo_layout.addStretch(2)
        stamp = QLabel("✓")
        stamp.setObjectName("stampArt")
        stamp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stamp.setFixedSize(110, 110)
        stamp.setStyleSheet(
            "color:#a7efb6;background:rgba(255,255,255,0.07);"
            "border:1px solid #8064d4;border-radius:55px;font-size:42px;"
        )
        promo_layout.addWidget(stamp, 0, Qt.AlignmentFlag.AlignHCenter)
        promo_layout.addStretch(2)
        important = QFrame()
        important.setObjectName("loginImportant")
        important.setStyleSheet(
            "QFrame#loginImportant{background:rgba(255,255,255,0.10);"
            "border:1px solid rgba(255,255,255,0.13);border-radius:8px;}"
        )
        important_layout = QVBoxLayout(important)
        note_title = QLabel("ⓘ  IMPORTANTE")
        note_title.setStyleSheet("color:white;font-size:10px;font-weight:800;")
        note_text = QLabel("Acesso restrito a colaboradores autorizados.\nSuas ações são registradas e monitoradas.")
        note_text.setStyleSheet("color:#ddd6ff;font-size:10px;")
        important_layout.addWidget(note_title)
        important_layout.addWidget(note_text)
        promo_layout.addWidget(important)
        root.addWidget(promo, 5)

        panel = QWidget()
        panel.setStyleSheet("background:#faf9fc;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(42, 32, 42, 32)
        panel_layout.addStretch()
        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(470)
        card.setStyleSheet("QFrame#card{background:white;border:1px solid #ece9f2;border-radius:15px;}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 34, 40, 25)
        card_layout.setSpacing(13)
        card_brand = QHBoxLayout()
        card_brand.addWidget(BrandMark())
        card_company = QLabel("KROMBERG\n& SCHUBERT")
        card_company.setStyleSheet("font-size:16px;font-weight:850;color:#211b43;")
        card_brand.addWidget(card_company)
        card_brand.addStretch()
        card_layout.addLayout(card_brand)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color:{LINE};")
        card_layout.addWidget(divider)
        card_layout.addSpacing(8)
        card_layout.addWidget(eyebrow("Acesso seguro"))
        heading = QLabel("Entre no sistema")
        heading.setStyleSheet("font-size:27px;font-weight:800;color:#211b43;")
        card_layout.addWidget(heading)
        hint = QLabel("Use seus dados corporativos para continuar.")
        hint.setObjectName("muted")
        card_layout.addWidget(hint)
        card_layout.addSpacing(14)
        card_layout.addWidget(self._field_label("CHAPA"))
        self.chapa = QLineEdit()
        self.chapa.setPlaceholderText("Digite sua chapa")
        self.chapa.setClearButtonEnabled(True)
        self.chapa.setMaxLength(30)
        self.chapa.returnPressed.connect(lambda: self.password.setFocus())
        card_layout.addWidget(self.chapa)
        card_layout.addWidget(self._field_label("SENHA"))
        self.password = QLineEdit()
        self.password.setPlaceholderText("Digite sua senha")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self._authenticate)
        card_layout.addWidget(self.password)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:#ba3045;font-size:11px;")
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)
        login_button = make_button("↪   Entrar")
        login_button.setMinimumHeight(43)
        login_button.clicked.connect(self._authenticate)
        card_layout.addWidget(login_button)
        self.demo_access_label = None
        if self.service.mode == "demonstração":
            demo = QLabel(
                "ACESSOS DE DEMONSTRAÇÃO\n"
                "Operador · Chapa 654321 · Senha 1234\n"
                "Administrador · Chapa 123456 · Senha 1234"
            )
            demo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            demo.setStyleSheet(
                "color:#624ca8;background:#f2efff;border-radius:6px;"
                "padding:9px;font-size:10px;"
            )
            card_layout.addWidget(demo)
            self.demo_access_label = demo
        footer = QLabel(f"Versão 1.2.0  ·  Ambiente {self.service.mode}")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color:#9b98a8;font-size:9px;margin-top:8px;")
        card_layout.addWidget(footer)
        panel_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        panel_layout.addStretch()
        root.addWidget(panel, 5)

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def _authenticate(self):
        chapa = self.chapa.text().strip()
        password = self.password.text()
        if not chapa or not password:
            self.error_label.setText("Informe sua chapa e senha.")
            return
        try:
            user = self.service.authenticate(chapa, password)
        except Exception as exc:
            self.error_label.setText(f"Não foi possível consultar o banco: {exc}")
            return
        if not user:
            self.error_label.setText("Chapa ou senha inválida.")
            self.password.clear()
            self.password.setFocus()
            return
        self.error_label.clear()
        self.authenticated.emit()


class MetricCard(QFrame):
    def __init__(self, icon, value, label, tone="#eeeaff"):
        super().__init__()
        self.setObjectName("card")
        row = QHBoxLayout(self)
        row.setContentsMargins(15, 13, 15, 13)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(38, 38)
        icon_label.setStyleSheet(
            f"background:{tone};color:{PURPLE};border-radius:9px;font-size:17px;font-weight:800;"
        )
        row.addWidget(icon_label)
        stack = QVBoxLayout()
        stack.setSpacing(2)
        value_label = QLabel(str(value))
        value_label.setObjectName("metricValue")
        caption = QLabel(label)
        caption.setObjectName("metricCaption")
        stack.addWidget(value_label)
        stack.addWidget(caption)
        row.addLayout(stack)
        row.addStretch()


class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.nav_buttons = {}
        self.setWindowTitle("Carimbo+ · Sistema de ocorrências")
        self.setMinimumSize(1080, 700)
        self.resize(1440, 900)
        self._build()
        self.show_page("Início" if self.service.is_admin() else "Nova ocorrência")

    def _build(self):
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        self.sidebar = self._build_sidebar()
        shell.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._build_topbar())
        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._new_occurrence_page())
        self.pages.addWidget(self._requests_page())
        self.pages.addWidget(self._notifications_page())
        self.pages.addWidget(self._how_page())
        right_layout.addWidget(self.pages, 1)
        shell.addWidget(right, 1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(232)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 19, 14, 15)
        layout.setSpacing(8)
        brand_row = QHBoxLayout()
        brand_row.addWidget(BrandMark(light=True))
        brand_stack = QVBoxLayout()
        title = QLabel("CARIMBO+")
        title.setObjectName("brandTitle")
        subtitle = QLabel("Gestão Inteligente de Carimbos")
        subtitle.setObjectName("brandSubtitle")
        brand_stack.addWidget(title)
        brand_stack.addWidget(subtitle)
        brand_row.addLayout(brand_stack)
        layout.addLayout(brand_row)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(
            "color:rgba(255,255,255,0.15);margin-top:15px;margin-bottom:14px;"
        )
        layout.addWidget(separator)
        items = [
            ("Início", "⌂"),
            ("Nova ocorrência", "＋"),
            ("Minhas solicitações", "▤"),
        ]
        if self.service.is_admin():
            items.append(("Central de notificações", "♧"))
        items.append(("Como funciona?", "?"))
        for name, icon in items:
            button = QPushButton(f"{icon}    {name}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, page=name: self.show_page(page))
            layout.addWidget(button)
            self.nav_buttons[name] = button
        layout.addStretch()
        user = self.service.current_user or {}
        safe_name = user.get("name", "Colaborador")
        profile_note = QLabel(f"⌾  Área segura\n\n{safe_name}\nChapa {user.get('chapa', '—')}\n\nAs ações são registradas para auditoria.")
        profile_note.setWordWrap(True)
        profile_note.setStyleSheet(
            "color:#d3c9f4;background:rgba(255,255,255,0.05);"
            "border:1px solid rgba(255,255,255,0.13);border-radius:9px;"
            "padding:12px;font-size:10px;"
        )
        layout.addWidget(profile_note)
        logout = QPushButton("↪    Sair do sistema")
        logout.setObjectName("logoutButton")
        logout.clicked.connect(self.logout)
        layout.addWidget(logout)
        return sidebar

    def _build_topbar(self):
        bar = QFrame()
        bar.setObjectName("topbar")
        bar.setFixedHeight(66)
        row = QHBoxLayout(bar)
        row.setContentsMargins(22, 0, 24, 0)
        title = QLabel("SISTEMA DE OCORRÊNCIAS DE CARIMBO")
        title.setObjectName("topbarTitle")
        row.addWidget(title)
        row.addStretch()
        user = self.service.current_user or {}
        avatar = QLabel(user.get("name", "U")[:2].upper())
        avatar.setObjectName("avatar")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(avatar)
        details = QVBoxLayout()
        name = QLabel(f"Chapa: {user.get('chapa', '—')}")
        name.setStyleSheet("font-size:10px;font-weight:800;")
        role = QLabel("Administrador" if self.service.is_admin() else "Operador")
        role.setStyleSheet("font-size:9px;color:#898599;")
        details.addWidget(name)
        details.addWidget(role)
        row.addLayout(details)
        return bar

    def _scroll_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(27, 23, 27, 28)
        layout.setSpacing(17)
        scroll.setWidget(host)
        return scroll, layout

    def _dashboard_page(self):
        scroll, layout = self._scroll_page()
        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(26, 22, 26, 22)
        copy = QVBoxLayout()
        copy.addWidget(eyebrow("CONTROLE E RASTREABILIDADE"))
        title = QLabel("Sistema para <span style='color:#79df99'>ocorrências<br>de carimbo</span>")
        title.setObjectName("heroTitle")
        copy.addWidget(title)
        body = QLabel("Registre, acompanhe e mantenha o controle dos carimbos da sua operação.")
        body.setObjectName("heroBody")
        body.setWordWrap(True)
        body.setMaximumWidth(500)
        copy.addWidget(body)
        hero_layout.addLayout(copy, 1)
        stamp_panel = QFrame()
        stamp_panel.setObjectName("heroStampPanel")
        stamp_panel.setStyleSheet(
            "QFrame#heroStampPanel{background:rgba(255,255,255,0.05);"
            "border:1px solid rgba(255,255,255,0.14);border-radius:12px;}"
        )
        stamp_layout = QVBoxLayout(stamp_panel)
        stamp_layout.setContentsMargins(12, 10, 12, 10)
        stamp_layout.setSpacing(5)
        stamp_mark = QLabel("✓")
        stamp_mark.setObjectName("stampArt")
        stamp_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stamp_mark.setFixedSize(58, 58)
        stamp_mark.setStyleSheet(
            "color:#a7efb6;background:#382091;border:1px solid #8064d4;"
            "border-radius:29px;font-size:27px;font-weight:800;"
        )
        stamp_caption = QLabel("CARIMBO\nCONTROLADO")
        stamp_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stamp_caption.setStyleSheet("color:#e4dcff;font-size:8px;font-weight:800;")
        stamp_layout.addWidget(stamp_mark, 0, Qt.AlignmentFlag.AlignHCenter)
        stamp_layout.addWidget(stamp_caption)
        stamp_panel.setFixedSize(104, 105)
        hero_layout.addWidget(stamp_panel)
        layout.addWidget(hero)

        section_row = QHBoxLayout()
        section_row.addWidget(eyebrow("FLUXO RÁPIDO"))
        section_row.addStretch()
        section_row.addWidget(QLabel("Abra uma solicitação em poucos passos"))
        layout.addLayout(section_row)
        quick_grid = QGridLayout()
        quick_grid.setSpacing(11)
        quick_data = [
            ("♙", "Funcionário novo", "Solicitar carimbo para novo colaborador.", "#27a36b"),
            ("▣", "Carimbo perdido", "Registrar ocorrência de perda do carimbo.", "#d84252"),
            ("♜", "Carimbo danificado", "Registrar carimbo danificado ou ilegível.", "#dda91c"),
            ("↻", "Troca de carimbo", "Solicitar troca do carimbo atual.", "#356cce"),
        ]
        for index, (icon, title, desc, color) in enumerate(quick_data):
            card = QFrame()
            card.setObjectName("quickCard")
            card.setMinimumHeight(146)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            button = QPushButton()
            button.setObjectName("quickButton")
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            inner = QVBoxLayout(button)
            inner.setContentsMargins(14, 11, 14, 11)
            inner.setSpacing(5)
            symbol = QLabel(icon)
            symbol.setFixedHeight(31)
            symbol.setStyleSheet(f"color:{color};font-size:27px;font-weight:800;")
            label = QLabel(title)
            label.setMinimumHeight(18)
            label.setStyleSheet("font-size:12px;font-weight:800;")
            subtitle = QLabel(desc)
            subtitle.setWordWrap(True)
            subtitle.setMinimumHeight(30)
            subtitle.setStyleSheet("color:#777488;font-size:10px;")
            inner.addWidget(symbol)
            inner.addWidget(label)
            inner.addWidget(subtitle)
            button.clicked.connect(
                lambda checked=False, occurrence=title: self.show_page(
                    "Nova ocorrência", preset_type=occurrence
                )
            )
            card_layout.addWidget(button)
            quick_grid.addWidget(card, 0, index)
        layout.addLayout(quick_grid)

        table_heading = QHBoxLayout()
        title = QLabel("Ocorrências recentes")
        title.setObjectName("sectionTitle")
        table_heading.addWidget(title)
        table_heading.addStretch()
        more = make_button("Ver todas   ›", primary=False)
        more.clicked.connect(lambda: self.show_page("Minhas solicitações"))
        table_heading.addWidget(more)
        layout.addLayout(table_heading)
        records = self.service.occurrences()[:5]
        rows = [
            (
                item["protocol"],
                item["collaborator"],
                item["type"],
                item["created_at"],
                item["status"],
            )
            for item in records
        ]
        table = make_table(
            ["Protocolo", "Colaborador", "Tipo", "Data/hora", "Status"],
            rows,
            min_height=205,
        )
        table.setColumnWidth(0, 125)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 155)
        table.setColumnWidth(3, 130)
        layout.addWidget(table)

        info_row = QHBoxLayout()
        for icon, title, detail, color in [
            ("✓", "Termo de responsabilidade", "Uso consciente e rastreável.", "#6041bd"),
            ("♧", "Notificações automáticas", "Responsáveis acompanham cada ação.", "#3668c5"),
            ("⌾", "Segurança e controle", "Informações registradas para auditoria.", "#26915a"),
        ]:
            info = QFrame()
            info.setObjectName("card")
            info_layout = QHBoxLayout(info)
            info_layout.setContentsMargins(12, 10, 12, 10)
            badge = QLabel(icon)
            badge.setStyleSheet(f"color:{color};background:#f1edff;border-radius:14px;font-size:14px;font-weight:800;")
            badge.setFixedSize(28, 28)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text = QVBoxLayout()
            text.addWidget(QLabel(f"<b>{title}</b>"))
            small = QLabel(detail)
            small.setStyleSheet("color:#817d8e;font-size:9px;")
            text.addWidget(small)
            info_layout.addWidget(badge)
            info_layout.addLayout(text)
            info_row.addWidget(info)
        layout.addLayout(info_row)
        layout.addStretch()
        return scroll

    def _new_occurrence_page(self):
        scroll, layout = self._scroll_page()
        layout.addWidget(page_title("Nova ocorrência", "Informe os dados para abrir uma solicitação de carimbo."))
        card = QFrame()
        card.setObjectName("formCard")
        form = QVBoxLayout(card)
        form.setContentsMargins(23, 21, 23, 23)
        form.setSpacing(12)
        form_header = QHBoxLayout()
        number = QLabel("01")
        number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number.setFixedSize(40, 40)
        number.setStyleSheet("color:#5a32c5;background:#eeeaff;border-radius:10px;font-weight:800;")
        header_text = QVBoxLayout()
        section = QLabel("Detalhes da ocorrência")
        section.setObjectName("sectionTitle")
        small = QLabel("Preencha os campos abaixo com atenção.")
        small.setObjectName("muted")
        header_text.addWidget(section)
        header_text.addWidget(small)
        form_header.addWidget(number)
        form_header.addLayout(header_text)
        form_header.addStretch()
        form.addLayout(form_header)
        row = QHBoxLayout()
        type_column = QVBoxLayout()
        type_column.addWidget(self._label("TIPO DE OCORRÊNCIA"))
        self.occurrence_type = QComboBox()
        allowed_types = (
            OCCURRENCE_TYPES
            if self.service.is_admin()
            else OPERATOR_OCCURRENCE_TYPES
        )
        self.occurrence_type.addItems(allowed_types)
        type_column.addWidget(self.occurrence_type)
        priority_column = QVBoxLayout()
        priority_column.addWidget(self._label("PRIORIDADE"))
        self.priority = QComboBox()
        self.priority.addItems(PRIORITIES)
        self.priority.setCurrentText(DEFAULT_PRIORITY)
        self.priority_info = None
        if self.service.is_admin():
            priority_column.addWidget(self.priority)
        else:
            self.priority_info = QLabel(
                "A prioridade inicial será definida pelo administrador."
            )
            self.priority_info.setObjectName("muted")
            self.priority_info.setWordWrap(True)
            priority_column.addWidget(self.priority_info)
        row.addLayout(type_column, 2)
        row.addLayout(priority_column, 1)
        form.addLayout(row)
        form.addWidget(self._label("COLABORADOR"))
        self.collaborator = QLineEdit()
        self.collaborator.setText(self.service.current_user["name"])
        form.addWidget(self.collaborator)
        form.addWidget(self._label("DESCRIÇÃO *"))
        self.description = QTextEdit()
        self.description.setPlaceholderText(
            "Descreva o que aconteceu e qualquer informação importante..."
        )
        self.description.setMinimumHeight(145)
        form.addWidget(self.description)
        actions = QHBoxLayout()
        actions.addStretch()
        clear_button = make_button("Limpar", primary=False)
        clear_button.clicked.connect(self._clear_occurrence_form)
        save_button = make_button("Registrar ocorrência   ↗")
        save_button.clicked.connect(self._save_occurrence)
        actions.addWidget(clear_button)
        actions.addWidget(save_button)
        form.addLayout(actions)
        layout.addWidget(card)
        layout.addStretch()
        return scroll

    def _requests_page(self):
        scroll, layout = self._scroll_page()
        heading = QHBoxLayout()
        heading.addWidget(page_title(
            "Solicitações da equipe" if self.service.is_admin() else "Minhas solicitações",
            "Acompanhe o andamento de cada ocorrência registrada.",
        ), 1)
        create = make_button("＋ Nova ocorrência")
        create.clicked.connect(lambda: self.show_page("Nova ocorrência"))
        heading.addWidget(create, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(heading)
        card = QFrame()
        card.setObjectName("tableCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(15, 12, 15, 0)
        self.requests_count = QLabel("Solicitações")
        self.requests_count.setStyleSheet("font-weight:800;")
        toolbar.addWidget(self.requests_count)
        toolbar.addStretch()
        refresh = make_button("↻ Atualizar", primary=False)
        refresh.clicked.connect(self._refresh_requests)
        toolbar.addWidget(refresh)
        card_layout.addLayout(toolbar)
        self.requests_table = make_table(
            ["Protocolo", "Colaborador", "Chapa", "Tipo", "Prioridade", "Data/hora", "Status"],
            [],
            360,
        )
        self.request_protocol = None
        self._request_records_by_protocol = {}
        self.request_admin_panel = None
        card_layout.addWidget(self.requests_table)
        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(card, 1)
        if self.service.is_admin():
            self.requests_table.setSelectionMode(
                QTableWidget.SelectionMode.SingleSelection
            )
            self.requests_table.itemSelectionChanged.connect(
                self._load_selected_request
            )
            self.request_admin_panel = self._build_request_admin_panel()
            body.addWidget(self.request_admin_panel)
        layout.addLayout(body)
        layout.addStretch()
        return scroll

    def _build_request_admin_panel(self):
        panel = QFrame()
        panel.setObjectName("card")
        panel.setFixedWidth(300)
        form = QVBoxLayout(panel)
        form.setContentsMargins(17, 17, 17, 17)
        form.setSpacing(10)
        title = QLabel("Gerenciar solicitação")
        title.setObjectName("sectionTitle")
        form.addWidget(title)
        self.request_protocol_label = QLabel("Selecione uma solicitação na tabela.")
        self.request_protocol_label.setWordWrap(True)
        self.request_protocol_label.setObjectName("muted")
        form.addWidget(self.request_protocol_label)
        form.addWidget(self._label("DESCRIÇÃO DA SOLICITAÇÃO"))
        self.request_description = QTextEdit()
        self.request_description.setReadOnly(True)
        self.request_description.setPlaceholderText("Nenhuma descrição informada.")
        self.request_description.setFixedHeight(120)
        form.addWidget(self.request_description)
        form.addWidget(self._label("PRIORIDADE"))
        self.request_priority = QComboBox()
        self.request_priority.addItems(PRIORITIES)
        form.addWidget(self.request_priority)
        form.addWidget(self._label("STATUS"))
        self.request_status = QComboBox()
        self.request_status.addItems(STATUSES)
        self.request_status.currentIndexChanged.connect(
            self._sync_request_save_enabled
        )
        form.addWidget(self.request_status)
        form.addStretch()
        self.save_request_button = make_button("Salvar alterações")
        self.save_request_button.setEnabled(False)
        self.save_request_button.clicked.connect(self._save_request_changes)
        form.addWidget(self.save_request_button)
        return panel

    def _notifications_page(self):
        scroll, layout = self._scroll_page()
        layout.addWidget(page_title("Central de notificações", "Gerencie todas as notificações do sistema."))
        metrics = QHBoxLayout()
        self.notification_metrics = [
            MetricCard("♧", 0, "Novas"),
            MetricCard("⌛", 0, "Pendentes", "#fff5dc"),
            MetricCard("✓", 0, "Resolvidas", "#e7f8ed"),
            MetricCard("▣", 0, "Arquivadas"),
        ]
        for metric in self.notification_metrics:
            metrics.addWidget(metric)
        layout.addLayout(metrics)
        body = QHBoxLayout()
        card = QFrame()
        card.setObjectName("tableCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel("Lista de notificações")
        heading.setObjectName("sectionTitle")
        heading.setContentsMargins(15, 14, 0, 0)
        card_layout.addWidget(heading)
        self.notifications_table = make_table(
            ["Protocolo", "Colaborador", "Tipo", "Data/hora", "Prioridade", "Status"],
            [],
            420,
        )
        card_layout.addWidget(self.notifications_table)
        body.addWidget(card, 1)
        audit = QFrame()
        audit.setObjectName("card")
        audit.setFixedWidth(220)
        audit_layout = QVBoxLayout(audit)
        audit_layout.setContentsMargins(17, 17, 17, 17)
        audit_layout.addWidget(eyebrow("AUDITORIA"))
        audit_title = QLabel("Segurança e controle")
        audit_title.setObjectName("sectionTitle")
        audit_layout.addWidget(audit_title)
        audit_text = QLabel(
            "Cada ação fica registrada para consulta dos responsáveis.\n\n"
            "✓  Login e acessos rastreados\n\n"
            "✓  Alterações com data e hora\n\n"
            "✓  Dados protegidos por perfil"
        )
        audit_text.setWordWrap(True)
        audit_text.setObjectName("muted")
        audit_layout.addWidget(audit_text)
        audit_layout.addStretch()
        body.addWidget(audit)
        layout.addLayout(body)
        layout.addStretch()
        return scroll

    def _how_page(self):
        scroll, layout = self._scroll_page()
        layout.addWidget(page_title("Como funciona?", "O fluxo de controle de carimbos em poucos passos."))
        steps = QHBoxLayout()
        for number, title, text in [
            ("01", "Registre", "Abra uma ocorrência para carimbo novo, perdido, danificado ou troca."),
            ("02", "Acompanhe", "Consulte o protocolo e veja o status da solicitação."),
            ("03", "Conclua", "O responsável atualiza o andamento e preserva o histórico."),
        ]:
            card = QFrame()
            card.setObjectName("card")
            card.setMinimumHeight(190)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 18, 20, 18)
            number_label = QLabel(number)
            number_label.setStyleSheet("color:#6b3dd0;font-size:12px;font-weight:800;")
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size:17px;font-weight:800;")
            detail = QLabel(text)
            detail.setWordWrap(True)
            detail.setObjectName("muted")
            card_layout.addWidget(number_label)
            card_layout.addSpacing(12)
            card_layout.addWidget(title_label)
            card_layout.addWidget(detail)
            card_layout.addStretch()
            steps.addWidget(card)
        layout.addLayout(steps)
        layout.addStretch()
        return scroll

    @staticmethod
    def _label(text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def show_page(self, name, preset_type=None):
        page_map = {
            "Início": 0,
            "Nova ocorrência": 1,
            "Minhas solicitações": 2,
            "Solicitações da equipe": 2,
            "Central de notificações": 3,
            "Como funciona?": 4,
        }
        if name == "Central de notificações" and not self.service.is_admin():
            QMessageBox.warning(self, "Acesso restrito", "Esta área é exclusiva para responsáveis autorizados.")
            return
        if name == "Solicitações da equipe" and not self.service.is_admin():
            name = "Minhas solicitações"
        self.pages.setCurrentIndex(page_map.get(name, 0))
        nav_name = "Minhas solicitações" if name == "Solicitações da equipe" else name
        for nav, button in self.nav_buttons.items():
            button.setChecked(nav == nav_name)
        if name in {"Minhas solicitações", "Solicitações da equipe"}:
            self._refresh_requests()
        elif name == "Central de notificações":
            self._refresh_notifications()
        if preset_type:
            self.occurrence_type.setCurrentText(preset_type)

    def _refresh_requests(self):
        try:
            records = self.service.occurrences()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar as solicitações:\n{exc}")
            records = []
        if self.request_admin_panel:
            self.request_protocol = None
            self.request_protocol_label.setText("Selecione uma solicitação na tabela.")
            self.request_description.clear()
            self.save_request_button.setEnabled(False)
        self._request_records_by_protocol = {
            item["protocol"]: item for item in records
        }
        self.requests_count.setText(f"{len(records)} registro(s)")
        rows = [
            (
                item["protocol"],
                item["collaborator"],
                item["chapa"],
                item["type"],
                item["priority"],
                item["created_at"],
                item["status"],
            )
            for item in records
        ]
        self._fill_table(self.requests_table, rows)

    @staticmethod
    def _status_for_editor(status):
        if status in STATUSES:
            return status
        normalized = str(status).strip().casefold()
        if normalized in {
            "em análise",
            "em analise",
            "novo",
            "aberto",
        }:
            return "Em andamento"
        if normalized in {
            "concluido",
            "concluído",
            "finalizado",
            "carimbo entregue",
            "termo assinado",
        }:
            return "Concluído"
        return None

    def _load_selected_request(self):
        if not self.service.is_admin() or not self.request_admin_panel:
            return
        row = self.requests_table.currentRow()
        if row < 0 or self.requests_table.item(row, 0) is None:
            self.request_protocol = None
            self.request_protocol_label.setText("Selecione uma solicitação na tabela.")
            self.save_request_button.setEnabled(False)
            return
        self.request_protocol = self.requests_table.item(row, 0).text()
        collaborator = self.requests_table.item(row, 1).text()
        record = self._request_records_by_protocol.get(self.request_protocol, {})
        self.request_description.setPlainText(
            record.get("description") or "Nenhuma descrição informada."
        )
        status = self._status_for_editor(self.requests_table.item(row, 6).text())
        if status is None:
            self.request_protocol_label.setText(
                f"{self.request_protocol}\n{collaborator}\n"
                "Status antigo: escolha uma opção atual para salvar."
            )
            self.request_status.setCurrentIndex(-1)
        else:
            self.request_protocol_label.setText(
                f"{self.request_protocol}\n{collaborator}"
            )
            self.request_status.setCurrentText(status)
        priority = self.requests_table.item(row, 4).text()
        if priority not in PRIORITIES:
            priority = DEFAULT_PRIORITY
        self.request_priority.setCurrentText(priority)
        self._sync_request_save_enabled()

    def _sync_request_save_enabled(self):
        self.save_request_button.setEnabled(
            bool(
                self.service.is_admin()
                and self.request_protocol
                and self.request_status.currentText() in STATUSES
            )
        )

    def _save_request_changes(self):
        if (
            not self.service.is_admin()
            or not self.request_protocol
            or self.request_status.currentText() not in STATUSES
        ):
            return
        try:
            self.service.update_occurrence(
                self.request_protocol,
                self.request_priority.currentText(),
                self.request_status.currentText(),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Falha ao atualizar",
                f"Não foi possível salvar as alterações:\n{exc}",
            )
            return
        QMessageBox.information(
            self,
            "Solicitação atualizada",
            f"A solicitação {self.request_protocol} foi atualizada.",
        )
        self._refresh_requests()

    def _refresh_notifications(self):
        try:
            records = self.service.occurrences(all_records=True)
            stats = self.service.stats()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar as notificações:\n{exc}")
            records, stats = [], {"new": 0, "pending": 0, "resolved": 0, "archived": 0}
        for card, value in zip(
            self.notification_metrics,
            [stats["new"], stats["pending"], stats["resolved"], stats["archived"]],
        ):
            value_label = card.findChild(QLabel, "metricValue")
            if value_label:
                value_label.setText(str(value))
        self._fill_table(
            self.notifications_table,
            [
                (
                    item["protocol"],
                    item["collaborator"],
                    item["type"],
                    item["created_at"],
                    item["priority"],
                    item["status"],
                )
                for item in records
            ],
        )

    @staticmethod
    def _fill_table(table, rows):
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                if col_index == len(row) - 1:
                    if value in {"Concluído", "Finalizado"}:
                        color = Qt.GlobalColor.darkGreen
                    else:
                        color = Qt.GlobalColor.darkBlue
                    item.setForeground(color)
                table.setItem(row_index, col_index, item)
        table.resizeColumnsToContents()

    def _clear_occurrence_form(self):
        self.occurrence_type.setCurrentIndex(0)
        self.priority.setCurrentText(DEFAULT_PRIORITY)
        self.collaborator.setText(self.service.current_user["name"])
        self.description.clear()

    def _save_occurrence(self):
        occurrence_type = self.occurrence_type.currentText().strip()
        description = self.description.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Campo obrigatório", "Descreva a ocorrência antes de registrar.")
            self.description.setFocus()
            return
        try:
            created = self.service.create_occurrence(
                occurrence_type,
                description,
                self.priority.currentText(),
                self.collaborator.text().strip() or None,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Falha ao registrar", str(exc))
            return
        QMessageBox.information(
            self,
            "Ocorrência registrada",
            f"A solicitação {created['protocol']} foi registrada com sucesso.",
        )
        self._clear_occurrence_form()
        self.show_page("Minhas solicitações")

    def logout(self):
        answer = QMessageBox.question(
            self,
            "Sair do sistema",
            "Deseja encerrar sua sessão?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.service.logout()
            self.close()
            self.login_window = LoginWindow(self.service)
            self.login_window.authenticated.connect(self._reopen_main)
            self.login_window.show()

    def _reopen_main(self):
        self.login_window.close()
        self.main_window = MainWindow(self.service)
        self.main_window.show()


class DesktopApplication:
    def __init__(self, service=None):
        self.service = service or StampControlService()
        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        self.qt_app.setApplicationName("Carimbo+")
        self.qt_app.setOrganizationName("Kromberg & Schubert")
        self.qt_app.setFont(QFont("Inter", 10))
        self.qt_app.setStyle("Fusion")
        self.qt_app.setStyleSheet(APP_STYLESHEET)
        self.login_window = None
        self.main_window = None

    def start(self):
        self.login_window = LoginWindow(self.service)
        self.login_window.authenticated.connect(self.open_main)
        self.login_window.show()
        return self.qt_app.exec()

    def open_main(self):
        self.login_window.close()
        self.main_window = MainWindow(self.service)
        self.main_window.show()


def run():
    application = DesktopApplication()
    return application.start()
