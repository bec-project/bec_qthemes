import sys
from pathlib import Path

from PySide6.QtWidgets import QLayout
from qtpy.QtWidgets import QDateEdit, QDateTimeEdit, QTimeEdit
from qtpy.QtCore import Qt, QDate, QDateTime, QTime, QSize
from qtpy.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel, QAction
from qtpy.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QToolBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QCommandLinkButton,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QSlider,
    QDial,
    QScrollBar,
    QProgressBar,
    QComboBox,
    QFontComboBox,
    QKeySequenceEdit,
    QListWidget,
    QListWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QListView,
    QTreeView,
    QTableView,
    QGroupBox,
    QFrame,
    QSplitter,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QCalendarWidget,
    QLCDNumber,
    QGraphicsView,
    QGraphicsScene,
    QMenuBar,
    QMenu,
    QStatusBar,
    QToolBar,
    QDockWidget,
    QFileDialog,
    QColorDialog,
    QFontDialog,
    QInputDialog,
    QErrorMessage,
    QMessageBox,
    QAbstractSpinBox,
)
from bec_qthemes import material_icon
from bec_qthemes.qss_editor.qss_editor import ThemeWidget
from bec_widgets.widgets.containers.dock import BECDockArea


def page_spinboxes_plus():
    panel = QWidget()
    outer = QVBoxLayout(panel)

    # Variants grid: normal vs disabled side-by-side
    grid_host = QWidget()
    grid = QGridLayout(grid_host)

    # 1) Standard arrows
    sb_arrows = QSpinBox()
    sb_arrows.setRange(-10, 10)
    grid.addWidget(QLabel("QSpinBox (arrows)"), 0, 0)
    grid.addWidget(sb_arrows, 1, 0)
    sb_arrows_dis = make_disabled_clone(sb_arrows)
    grid.addWidget(QLabel("disabled"), 0, 1)
    grid.addWidget(sb_arrows_dis, 1, 1)

    # 2) Plus/Minus symbols
    sb_pm = QSpinBox()
    sb_pm.setRange(-10, 10)
    sb_pm.setButtonSymbols(QAbstractSpinBox.PlusMinus)
    grid.addWidget(QLabel("QSpinBox (plus/minus)"), 2, 0)
    grid.addWidget(sb_pm, 3, 0)
    grid.addWidget(make_disabled_clone(sb_pm), 3, 1)

    # 3) No buttons (keyboard/mousewheel only)
    sb_nb = QSpinBox()
    sb_nb.setRange(0, 100)
    sb_nb.setButtonSymbols(QAbstractSpinBox.NoButtons)
    grid.addWidget(QLabel("QSpinBox (no buttons)"), 4, 0)
    grid.addWidget(sb_nb, 5, 0)
    grid.addWidget(make_disabled_clone(sb_nb), 5, 1)

    # 4) With prefix/suffix & accelerated
    sb_pref = QSpinBox()
    sb_pref.setRange(0, 1000)
    sb_pref.setSuffix(" ms")
    sb_pref.setAccelerated(True)
    grid.addWidget(QLabel("QSpinBox (suffix, accelerated)"), 6, 0)
    grid.addWidget(sb_pref, 7, 0)
    grid.addWidget(make_disabled_clone(sb_pref), 7, 1)

    # 5) Double spinbox with decimals and step
    dsb = QDoubleSpinBox()
    dsb.setRange(-100.0, 100.0)
    dsb.setDecimals(3)
    dsb.setSingleStep(0.125)
    grid.addWidget(QLabel("QDoubleSpinBox (decimals)"), 8, 0)
    grid.addWidget(dsb, 9, 0)
    grid.addWidget(make_disabled_clone(dsb), 9, 1)

    # 6) Wrapping & special value text
    sb_wrap = QSpinBox()
    sb_wrap.setRange(0, 3)
    sb_wrap.setWrapping(True)
    sb_wrap.setSpecialValueText("Off")
    grid.addWidget(QLabel("QSpinBox (wrapping, special)"), 10, 0)
    grid.addWidget(sb_wrap, 11, 0)
    grid.addWidget(make_disabled_clone(sb_wrap), 11, 1)

    # 7) Date/Time edits with calendar popup
    de = QDateEdit(QDate.currentDate())
    de.setCalendarPopup(True)
    dte = QDateTimeEdit(QDateTime.currentDateTime())
    dte.setCalendarPopup(True)
    grid.addWidget(QLabel("QDateEdit (calendar)"), 12, 0)
    grid.addWidget(de, 13, 0)
    grid.addWidget(make_disabled_clone(de), 13, 1)
    grid.addWidget(QLabel("QDateTimeEdit (calendar)"), 14, 0)
    grid.addWidget(dte, 15, 0)
    grid.addWidget(make_disabled_clone(dte), 15, 1)

    outer.addWidget(grid_host)
    outer.addStretch(1)
    return make_section("SpinBoxes+ (Variants)", panel)


def make_section(title: str, inner: QWidget) -> QWidget:
    box = QGroupBox(title)
    lay = QVBoxLayout(box)
    lay.addWidget(inner)
    return box


def make_grid(pairs):
    w = QWidget()
    g = QGridLayout(w)
    for r, (label, widget) in enumerate(pairs):
        if widget is None:
            widget = QLabel("–")
        if isinstance(widget, QLayout):
            container = QWidget()
            container.setLayout(widget)
            widget = container
        if label:
            g.addWidget(QLabel(label), r, 0)
            g.addWidget(widget, r, 1)
        else:
            g.addWidget(widget, r, 0, 1, 2)
    return w


class CollapsibleGroup(QWidget):
    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self._btn = QToolButton()
        self._btn.setText(title)
        self._btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._btn.setArrowType(Qt.DownArrow)
        self._btn.setCheckable(True)
        self._btn.setChecked(True)
        self._content = content
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lay.addWidget(self._btn)
        lay.addWidget(self._content)
        self._btn.toggled.connect(self._on_toggled)

    def _on_toggled(self, on: bool):
        self._content.setVisible(on)
        self._btn.setArrowType(Qt.DownArrow if on else Qt.RightArrow)


def make_disabled_clone(w: QWidget) -> QWidget:
    # Best-effort duplicate for showcase; simple, safe types only
    cls = type(w)
    try:
        clone = cls()
    except Exception:
        clone = QPushButton(w.metaObject().className())
    # Copy some common props
    if isinstance(w, (QPushButton, QToolButton, QCommandLinkButton, QLabel)):
        try:
            clone.setText(w.text())
        except Exception:
            pass
    if isinstance(w, (QCheckBox, QRadioButton)):
        clone.setText(w.text())
        clone.setChecked(w.isChecked())
    if isinstance(w, QLineEdit):
        clone.setText(w.text())
        clone.setPlaceholderText(w.placeholderText())
        clone.setClearButtonEnabled(w.isClearButtonEnabled())
    if isinstance(w, QPlainTextEdit):
        clone.setPlainText(w.toPlainText())
    if isinstance(w, QTextEdit):
        clone.setHtml(w.toHtml())
    if isinstance(w, QComboBox):
        for i in range(w.count()):
            clone.addItem(w.itemText(i))
        clone.setEditable(w.isEditable())
    if isinstance(w, (QSpinBox, QDoubleSpinBox)):
        clone.setRange(w.minimum(), w.maximum())
        clone.setValue(w.value())
    if isinstance(w, QSlider):
        clone.setOrientation(w.orientation())
        clone.setRange(w.minimum(), w.maximum())
        clone.setValue(w.value())
    if isinstance(w, QProgressBar):
        clone.setRange(w.minimum(), w.maximum())
        clone.setValue(w.value())
    clone.setEnabled(False)
    return clone


def page_groups_toolboxes():
    panel = QWidget()
    outer = QVBoxLayout(panel)

    # --- GroupBoxes ---
    # Outline
    gb_outline = QGroupBox("GroupBox — Outline")
    gb_outline.setProperty("titlePosition", "left")
    f1 = QFormLayout(gb_outline)
    f1.addRow("Name", QLineEdit("Alice"))
    f1.addRow("Age", QSpinBox())

    # Card variant
    gb_card = QGroupBox("GroupBox — Card")
    gb_card.setProperty("variant", "card")
    vcard = QVBoxLayout(gb_card)
    vcard.addWidget(QLabel("Some content in a card-like group box."))
    vcard.addWidget(QPushButton("Action"))

    # Tile variants (modern web-like tiles)
    gb_tile = QGroupBox("Installed")
    gb_tile.setProperty("variant", "tile")
    vtile = QVBoxLayout(gb_tile)
    vtile.addWidget(QLabel("Content"))

    gb_tile_check = QGroupBox("Tile — Checkable")
    gb_tile_check.setProperty("variant", "tile")
    gb_tile_check.setCheckable(True)
    gb_tile_check.setChecked(True)
    vtilec = QVBoxLayout(gb_tile_check)
    vtilec.addWidget(QLabel("Content"))

    gb_tile_frameless = QGroupBox("Tile — Frameless")
    gb_tile_frameless.setProperty("variant", "tile")
    gb_tile_frameless.setProperty("frameless", "true")
    vtilef = QVBoxLayout(gb_tile_frameless)
    vtilef.addWidget(QLabel("Content"))

    # Checkable + collapsible content
    inner = QWidget()
    fl = QFormLayout(inner)
    fl.addRow("Host", QLineEdit("localhost"))
    fl.addRow("Port", QSpinBox())
    gb_check = QGroupBox("GroupBox — Checkable (collapsible)")
    gb_check.setCheckable(True)
    gb_check.setChecked(True)
    gl = QVBoxLayout(gb_check)
    gl.addWidget(inner)
    gb_check.toggled.connect(inner.setVisible)

    # Collapsible header widget (non-GroupBox) for comparison
    coll = CollapsibleGroup("Collapsible Group (custom)", QLabel("Hidden/Shown content"))

    # Disabled mirrors
    grid = QGridLayout()
    r = 0
    for title, w in [
        ("Outline", gb_outline),
        ("Card", gb_card),
        ("Tile", gb_tile),
        ("Tile (checkable)", gb_tile_check),
        ("Tile (frameless)", gb_tile_frameless),
        ("Collapsible", coll),
    ]:
        grid.addWidget(QLabel(title + " (enabled)"), r, 0)
        grid.addWidget(QLabel(title + " (disabled)"), r, 1)
        r += 1
        grid.addWidget(w, r, 0)
        grid.addWidget(make_disabled_clone(w), r, 1)
        r += 1
    outer.addWidget(QLabel("GroupBoxes"))
    outer.addLayout(grid)

    # --- ToolBoxes ---
    tbx1 = QToolBox()
    tbx1.addItem(QLabel("Page 1"), "General")
    tbx1.addItem(QLabel("Page 2"), "Details")

    tbx2 = QToolBox()
    tbx2.addItem(QListWidget(), "List")
    tbx2.addItem(QTreeWidget(), "Tree")

    h = QHBoxLayout()
    h.addWidget(tbx1)
    h.addWidget(tbx2)
    outer.addWidget(QLabel("ToolBoxes"))
    outer.addLayout(h)

    outer.addStretch(1)
    return make_section("GroupBoxes & ToolBoxes", panel)


def page_inputs():
    # some buttons to show icons testing

    icon_home = material_icon("home", color="#ffffff")
    button_home = QPushButton("Home")
    button_home.setIcon(icon_home)

    # Buttons
    btn_push = QPushButton("QPushButton")
    btn_tool = QToolButton()
    btn_tool.setText("QToolButton")
    btn_tool.setToolButtonStyle(Qt.ToolButtonTextOnly)
    btn_cmd = QCommandLinkButton("QCommandLinkButton", "Secondary text")

    # ToolButton with menu
    tbtn_menu = QToolButton()
    tbtn_menu.setText("With Menu")
    tbtn_menu.setPopupMode(QToolButton.MenuButtonPopup)
    m = QMenu(tbtn_menu)
    m.addAction("Action A")
    m.addAction("Action B")
    m.addSeparator()
    m.addAction("Disabled").setEnabled(False)
    tbtn_menu.setMenu(m)

    # Checkable
    chk = QCheckBox("QCheckBox")
    r1, r2 = QRadioButton("Option A"), QRadioButton("Option B")
    rg = QButtonGroup()
    rg.addButton(r1), rg.addButton(r2)
    r1.setChecked(True)

    # Line edits and text
    le = QLineEdit()
    le.setPlaceholderText("QLineEdit with QCompleter")
    le.setClearButtonEnabled(True)
    completer_items = ["alpha", "beta", "gamma", "delta"]
    from qtpy.QtWidgets import QCompleter

    le.setCompleter(QCompleter(completer_items))
    ple = QPlainTextEdit("QPlainTextEdit")
    te = QTextEdit("QTextEdit")

    # Spin boxes
    sb = QSpinBox()
    sb.setRange(-100, 100)
    dsb = QDoubleSpinBox()
    dsb.setDecimals(3)
    dsb.setSingleStep(0.125)
    dsb.setSuffix(" V")

    # Sliders, Dial, Scrollbar, Progress
    sld = QSlider(Qt.Horizontal)
    sld_v = QSlider(Qt.Vertical)
    d = QDial()
    sbh = QScrollBar(Qt.Horizontal)
    pbar = QProgressBar()
    pbar.setRange(0, 100)
    sld.valueChanged.connect(pbar.setValue)
    # Indeterminate/busy progress
    pbar_busy = QProgressBar()
    pbar_busy.setRange(0, 0)

    # Combos
    cb = QComboBox()
    cb.addItems(["Item 1", "Item 2", "Item 3"])
    cb_edit = QComboBox()
    cb_edit.setEditable(True)
    cb_edit.addItems(["Edit me", "Type here"])
    fcb = QFontComboBox()

    # Key sequence edit
    kse = QKeySequenceEdit()

    pairs = [
        ("QPushButton-home", button_home),
        ("QPushButton", btn_push),
        ("QToolButton", btn_tool),
        ("QToolButton (menu)", tbtn_menu),
        ("QCommandLinkButton", btn_cmd),
        ("QCheckBox", chk),
        ("QRadioButton", make_grid([("", r1), ("", r2)])),
        ("QLineEdit", le),
        ("QPlainTextEdit", ple),
        ("QTextEdit", te),
        ("QSpinBox", sb),
        ("QDoubleSpinBox", dsb),
        ("QSlider", sld),
        ("QSlider (vertical)", sld_v),
        ("QDial", d),
        ("QScrollBar", sbh),
        ("QProgressBar (via slider)", pbar),
        ("QProgressBar (busy)", pbar_busy),
        ("QComboBox", cb),
        ("QComboBox (editable)", cb_edit),
        ("QFontComboBox", fcb),
        ("QKeySequenceEdit", kse),
    ]
    return make_section("Input Widgets", make_grid(pairs))


def page_buttons_plus():
    panel = QWidget()
    outer = QVBoxLayout(panel)

    # --- Gallery of variants ---
    grid_host = QWidget()
    grid = QGridLayout(grid_host)

    b_def = QPushButton("Default")
    b_default = QPushButton("Default (:default)")
    b_default.setDefault(True)

    b_flat = QPushButton("Flat")
    b_flat.setFlat(True)

    b_check = QPushButton("Checkable")
    b_check.setCheckable(True)

    b_primary = QPushButton("Primary")
    b_primary.setProperty("variant", "primary")

    b_outline = QPushButton("Outline")
    b_outline.setProperty("variant", "outline")

    b_ghost = QPushButton("Ghost")
    b_ghost.setProperty("variant", "ghost")

    b_danger = QPushButton("Danger")
    b_danger.setProperty("variant", "danger")

    b_success = QPushButton("Success")
    b_success.setProperty("variant", "success")

    samples = [
        (0, 0, b_def),
        (0, 1, b_default),
        (0, 2, b_flat),
        (0, 3, b_check),
        (1, 0, b_primary),
        (1, 1, b_outline),
        (1, 2, b_ghost),
        (1, 3, b_danger),
        (1, 4, b_success),
    ]
    for r, c, btn in samples:
        grid.addWidget(btn, r, c)

    outer.addWidget(QLabel("Button Variants Gallery"))
    outer.addWidget(grid_host)

    # --- Live tuner ---
    tuner = QGroupBox("Live Button Tuner")
    form = QFormLayout(tuner)

    tune_btn = QPushButton("Live Preview")

    cmb_variant = QComboBox()
    cmb_variant.addItem("(base)", "")
    for v in ["primary", "outline", "ghost", "danger", "success"]:
        cmb_variant.addItem(v, v)

    chk_default = QCheckBox("Default")
    chk_flat = QCheckBox("Flat")
    chk_checkable = QCheckBox("Checkable")
    chk_checked = QCheckBox("Checked")

    def re_polish(w: QWidget):
        s = w.style()
        s.unpolish(w)
        s.polish(w)
        w.update()

    def apply_variant():
        v = cmb_variant.currentData()
        if v:
            tune_btn.setProperty("variant", v)
        else:
            tune_btn.setProperty("variant", None)
        re_polish(tune_btn)

    def apply_states():
        tune_btn.setDefault(chk_default.isChecked())
        tune_btn.setFlat(chk_flat.isChecked())
        tune_btn.setCheckable(chk_checkable.isChecked())
        tune_btn.setChecked(chk_checked.isChecked())
        re_polish(tune_btn)

    cmb_variant.currentIndexChanged.connect(apply_variant)
    for cb in (chk_default, chk_flat, chk_checkable, chk_checked):
        cb.toggled.connect(apply_states)

    form.addRow("Variant", cmb_variant)
    form.addRow(
        "States",
        make_grid([("", chk_default), ("", chk_flat), ("", chk_checkable), ("", chk_checked)]),
    )
    form.addRow("Preview", tune_btn)

    outer.addWidget(tuner)
    outer.addStretch(1)
    return make_section("Buttons+ (Variants & Live Tuner)", panel)


def page_displays():
    # Labels (with pixmap)
    lbl_text = QLabel("QLabel (text)")
    pm = QPixmap(64, 64)
    pm.fill(Qt.gray)
    lbl_pix = QLabel("QLabel (pixmap below)")
    lbl_img = QLabel()
    lbl_img.setPixmap(pm)

    # LCD Number
    lcd = QLCDNumber()
    lcd.display(42)

    # Graphics View
    scene = QGraphicsScene()
    scene.addText("QGraphicsScene → QGraphicsView")
    gv = QGraphicsView(scene)
    gv.setMinimumHeight(120)

    # Frames
    lineH = QFrame()
    lineH.setFrameShape(QFrame.HLine)
    lineH.setFrameShadow(QFrame.Sunken)

    pairs = [
        ("QLabel (text)", lbl_text),
        ("QLabel (pixmap)", make_grid([("", lbl_pix), ("", lbl_img)])),
        ("QLCDNumber", lcd),
        ("QGraphicsView", gv),
        ("QFrame (HLine)", lineH),
    ]
    return make_section("Display Widgets", make_grid(pairs))


def page_containers():
    # GroupBox with inner layout
    inner = QWidget()
    inner_layout = QFormLayout(inner)
    inner_layout.addRow("Inside GroupBox:", QLineEdit())
    gb = QGroupBox("QGroupBox")
    gb_layout = QVBoxLayout(gb)
    gb_layout.addWidget(inner)

    # Splitter
    sp_left = QTextEdit("Left pane")
    sp_right = QTextEdit("Right pane")
    splitter = QSplitter()
    splitter.addWidget(sp_left)
    splitter.addWidget(sp_right)
    splitter.setSizes([150, 150])
    splitter.setMinimumHeight(120)

    # ScrollArea
    big_widget = QWidget()
    big_layout = QVBoxLayout(big_widget)
    for i in range(10):
        big_layout.addWidget(QPushButton(f"Button {i+1}"))
    sa = QScrollArea()
    sa.setWidget(big_widget)
    sa.setWidgetResizable(True)
    sa.setMinimumHeight(120)

    # Stacked and Tabs
    stacked = QStackedWidget()
    stacked.addWidget(QLabel("Stack page 1"))
    stacked.addWidget(QLabel("Stack page 2"))
    tabs = QTabWidget()
    tabs.addTab(QLabel("Tab 1"), "Tab 1")
    tabs.addTab(QLabel("Tab 2"), "Tab 2")

    pairs = [
        ("QGroupBox", gb),
        ("QSplitter", splitter),
        ("QScrollArea", sa),
        ("QStackedWidget", stacked),
        ("QTabWidget", tabs),
    ]
    return make_section("Container Widgets", make_grid(pairs))


def page_model_views():
    # Item-based widgets
    lw = QListWidget()
    for i in range(5):
        QListWidgetItem(f"Item {i+1}", lw)

    tw = QTreeWidget()
    tw.setHeaderLabels(["Name", "Value"])
    root = QTreeWidgetItem(["Root", "—"])
    for i in range(3):
        QTreeWidgetItem(root, [f"Child {i+1}", str(i)])
    tw.addTopLevelItem(root)
    tw.expandAll()

    tbl = QTableWidget(3, 3)
    for r in range(3):
        for c in range(3):
            tbl.setItem(r, c, QTableWidgetItem(f"({r},{c})"))

    # Model/View with QStandardItemModel
    model = QStandardItemModel(4, 3)
    model.setHorizontalHeaderLabels(["A", "B", "C"])
    for r in range(4):
        for c in range(3):
            item = QStandardItem(f"R{r}C{c}")
            model.setItem(r, c, item)

    lv = QListView()
    lv.setModel(model)
    tv = QTableView()
    tv.setModel(model)
    trv = QTreeView()
    trv.setModel(model)

    pairs = [
        ("QListWidget", lw),
        ("QTreeWidget", tw),
        ("QTableWidget", tbl),
        ("QListView (model)", lv),
        ("QTableView (model)", tv),
        ("QTreeView (model)", trv),
    ]
    return make_section("Item & Model/View Widgets", make_grid(pairs))


def page_datetime_misc():
    de = QDateEdit(QDate.currentDate())
    te = QTimeEdit(QTime.currentTime())
    dte = QDateTimeEdit(QDateTime.currentDateTime())
    cal = QCalendarWidget()
    cal.setGridVisible(True)

    pairs = [("QDateEdit", de), ("QTimeEdit", te), ("QDateTimeEdit", dte), ("QCalendarWidget", cal)]
    return make_section("Date/Time Widgets", make_grid(pairs))


def page_dialogs(parent_getter):
    # Buttons to launch common dialogs
    btn_file = QPushButton("QFileDialog.getOpenFileName")
    btn_color = QPushButton("QColorDialog.getColor")
    btn_font = QPushButton("QFontDialog.getFont")
    btn_input = QPushButton("QInputDialog.getText")
    btn_error = QPushButton("QErrorMessage")
    btn_msg = QPushButton("QMessageBox.information")

    def pick_file():
        QFileDialog.getOpenFileName(parent_getter(), "Pick a file")

    def pick_color():
        QColorDialog.getColor(parent=parent_getter(), title="Pick a color")

    def pick_font():
        QFontDialog.getFont(parent=parent_getter())

    def ask_text():
        QInputDialog.getText(parent_getter(), "Input", "Your name:")

    def show_error():
        dlg = QErrorMessage(parent_getter())
        dlg.showMessage("This is an example error message.")
        dlg.exec_()

    def show_msg():
        QMessageBox.information(parent_getter(), "Info", "Hello from QMessageBox!")

    btn_file.clicked.connect(pick_file)
    btn_color.clicked.connect(pick_color)
    btn_font.clicked.connect(pick_font)
    btn_input.clicked.connect(ask_text)
    btn_error.clicked.connect(show_error)
    btn_msg.clicked.connect(show_msg)

    pairs = [
        ("File dialog", btn_file),
        ("Color dialog", btn_color),
        ("Font dialog", btn_font),
        ("Input dialog", btn_input),
        ("Error message", btn_error),
        ("Message box", btn_msg),
    ]
    return make_section("Dialog Launchers", make_grid(pairs))


class WidgetZooWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Widget Zoo (qtpy)")
        self.resize(1200, 850)

        # Central toolbox
        self.toolbox = QToolBox()
        self.toolbox.setMinimumWidth(540)

        # Compose pages
        self.toolbox.addItem(page_inputs(), "Inputs")
        self.toolbox.addItem(page_buttons_plus(), "Buttons+")
        self.toolbox.addItem(page_spinboxes_plus(), "SpinBoxes+")
        self.toolbox.addItem(page_displays(), "Displays")
        self.toolbox.addItem(page_containers(), "Containers")
        self.toolbox.addItem(page_model_views(), "Model/View")
        self.toolbox.addItem(page_datetime_misc(), "Date/Time")
        self.toolbox.addItem(page_dialogs(lambda: self), "Dialogs")
        self.toolbox.addItem(page_groups_toolboxes(), "Groups & ToolBoxes")

        central = QWidget()
        lay = QHBoxLayout(central)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.toolbox)
        splitter.addWidget(self._make_right_side_panel())
        lay.addWidget(splitter)
        self.setCentralWidget(central)

        # Menus, toolbar, status
        self._build_menu_toolbar_status()
        self._add_dock_example()

    def _make_right_side_panel(self):
        # Create tab widget to organize components
        tabs = QTabWidget()

        # First tab: Live Preview / Playground
        preview_panel = QWidget()
        v = QVBoxLayout(preview_panel)
        v.setSpacing(8)

        lbl = QLabel("Live Preview / Playground")
        lbl.setStyleSheet("font-weight:600;")
        v.addWidget(lbl)

        # Progress controlled by slider
        self.preview_progress = QProgressBar()
        self.preview_progress.setRange(0, 100)
        v.addWidget(self.preview_progress)

        # Slider + dial synchronized
        self.preview_slider = QSlider(Qt.Horizontal)
        self.preview_dial = QDial()
        self.preview_slider.valueChanged.connect(self.preview_dial.setValue)
        self.preview_dial.valueChanged.connect(self.preview_slider.setValue)
        self.preview_slider.valueChanged.connect(self.preview_progress.setValue)

        v.addWidget(QLabel("Slider"))
        v.addWidget(self.preview_slider)
        v.addWidget(QLabel("Dial"))
        v.addWidget(self.preview_dial)
        chk_disable = QCheckBox("Disable left toolbox examples")
        chk_disable.toggled.connect(lambda on: self.toolbox.setEnabled(not on))
        v.addWidget(chk_disable)
        v.addStretch(1)

        # Second tab: Table Widget
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)

        self.tbl = QTableWidget(2, 2)
        self.tbl.setHorizontalHeaderLabels(["Key", "Value"])
        self.tbl.setItem(0, 0, QTableWidgetItem("A"))
        self.tbl.setItem(0, 1, QTableWidgetItem("1"))
        self.tbl.setItem(1, 0, QTableWidgetItem("B"))
        self.tbl.setItem(1, 1, QTableWidgetItem("2"))
        self.tbl.setMinimumHeight(140)

        table_layout.addWidget(QLabel("TableWidget"))
        table_layout.addWidget(self.tbl)
        table_layout.addStretch(1)

        # Third Tab ADS
        try:
            from bec_widgets.widgets.containers.advanced_dock_area.advanced_dock_area import (
                AdvancedDockArea,
            )

            ads_panel = QWidget()
            ads_layout = QVBoxLayout(ads_panel)
            self.ads = AdvancedDockArea()
            self.ads.new("Waveform")
            self.ads.new("ScanControl", where="right")
            ads_layout.addWidget(self.ads)
            tabs.addTab(ads_panel, "ADS")
        except ImportError:
            print("AdvancedDockArea not available, skipping ADS tab.")

        # Fourth Panel old Dock Area

        da_panel = QWidget()
        da_layout = QVBoxLayout(da_panel)
        self.dock_area = BECDockArea(self)
        da_layout.addWidget(self.dock_area)
        tabs.addTab(da_panel, "DockArea")
        self.dock_area.new(widget="Heatmap", position="left")
        self.dock_area.new(widget="ScanControl", position="right")

        # Add tabs
        tabs.addTab(preview_panel, "Preview")
        tabs.addTab(table_panel, "Table")

        return tabs

    def _build_menu_toolbar_status(self):
        menubar: QMenuBar = self.menuBar()
        file_menu: QMenu = menubar.addMenu("&File")
        view_menu: QMenu = menubar.addMenu("&View")
        help_menu: QMenu = menubar.addMenu("&Help")

        act_open = QAction("Open…", self)
        act_quit = QAction("Quit", self)
        act_about = QAction("About", self)
        act_toggle_status = QAction("Toggle Status Bar", self, checkable=True, checked=True)

        act_open.triggered.connect(lambda: QFileDialog.getOpenFileName(self, "Open…"))
        act_quit.triggered.connect(self.close)
        act_about.triggered.connect(
            lambda: QMessageBox.information(self, "About", "Qt Widget Zoo via qtpy")
        )
        act_toggle_status.toggled.connect(lambda v: self.statusBar().setVisible(v))

        file_menu.addAction(act_open)
        file_menu.addSeparator()
        file_menu.addAction(act_quit)
        view_menu.addAction(act_toggle_status)
        help_menu.addAction(act_about)

        tb: QToolBar = QToolBar("Main Toolbar", self)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)
        tb.addAction(act_open)
        tb.addAction(act_about)

        sb: QStatusBar = QStatusBar(self)
        self.setStatusBar(sb)
        sb.showMessage("Ready")

    def _add_dock_example(self):
        # List dock (existing)
        dock = QDockWidget("Dock: ListWidget", self)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        lw = QListWidget()
        for i in range(8):
            QListWidgetItem(f"Dock Item {i+1}", lw)
        dock.setWidget(lw)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Tree dock
        tree_dock = QDockWidget("Dock: Tree", self)
        tree_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        tree_view = QTreeView()
        tmodel = QStandardItemModel()
        tmodel.setHorizontalHeaderLabels(["Name", "Value"])
        root = QStandardItem("Root")
        child_a = QStandardItem("Child A")
        child_a_val = QStandardItem("42")
        child_b = QStandardItem("Child B")
        child_b_val = QStandardItem("hello")
        root.appendRow([child_a, child_a_val])
        root.appendRow([child_b, child_b_val])
        tmodel.appendRow([root, QStandardItem("—")])
        tree_view.setModel(tmodel)
        tree_view.expandAll()
        tree_dock.setWidget(tree_view)
        self.addDockWidget(Qt.LeftDockWidgetArea, tree_dock)

        # Table dock
        table_dock = QDockWidget("Dock: Table", self)
        table_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        table_view = QTableView()
        mdl = QStandardItemModel(5, 3)
        mdl.setHorizontalHeaderLabels(["A", "B", "C"])
        for r in range(5):
            for c in range(3):
                mdl.setItem(r, c, QStandardItem(f"R{r}C{c}"))
        table_view.setModel(mdl)
        table_dock.setWidget(table_view)
        self.addDockWidget(Qt.RightDockWidgetArea, table_dock)

        # Log dock (bottom)
        log_dock = QDockWidget("Dock: Log", self)
        log_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        log_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        log = QPlainTextEdit()
        log.setReadOnly(True)
        log.setPlainText("\n".join([f"[info] Sample log line {i+1}" for i in range(12)]))
        log_dock.setWidget(log)
        self.addDockWidget(Qt.BottomDockWidgetArea, log_dock)

        # Properties dock (left)
        prop_dock = QDockWidget("Dock: Properties", self)
        prop_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        prop = QWidget()
        form = QFormLayout(prop)
        form.addRow("Name", QLineEdit("Sample"))
        sp = QSpinBox()
        sp.setRange(0, 100)
        form.addRow("Count", sp)
        form.addRow("Enabled", QCheckBox())
        prop_dock.setWidget(prop)
        self.addDockWidget(Qt.LeftDockWidgetArea, prop_dock)


def main():
    SCRIPT_DIR = "/Users/janwyzula/PSI/bec_qthemes/bec_qthemes/qss_editor"
    THEME_QSS_PATH = SCRIPT_DIR + "/theme_base.qss"
    THEMES_DIR = SCRIPT_DIR + "/themes"

    app = QApplication(sys.argv)
    win = WidgetZooWindow()
    win.show()

    tool = ThemeWidget(qss_path=THEME_QSS_PATH, themes_dir=THEMES_DIR)
    tool.attach(target=None)  # application-wide
    tool.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
