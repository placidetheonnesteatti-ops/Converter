from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QComboBox,
    QCheckBox, QGroupBox, QVBoxLayout, QWidget, QTextEdit
)

from core.models import ConversionOptions, ConversionResult
from core.service import convert_file


class Worker(QObject):
    progress = Signal(str, int)
    finished = Signal(object)

    def __init__(self, source: Path, options: ConversionOptions):
        super().__init__()
        self.source = source
        self.options = options

    def run(self):
        try:
            result = convert_file(self.source, self.options, self._progress)
            self.finished.emit(result)
        except Exception as exc:
            self.finished.emit(ConversionResult(False, self.source, errors=[str(exc)]))

    def _progress(self, message: str, value: int):
        self.progress.emit(message, value)


class DropZone(QFrame):
    fileDropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        layout = QVBoxLayout(self)
        self.title = QLabel("Déposez un fichier DOCX ou PDF ici")
        self.title.setObjectName("dropTitle")
        self.subtitle = QLabel("ou cliquez sur « Choisir un fichier »")
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        self.setMinimumHeight(130)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.fileDropped.emit(urls[0].toLocalFile())
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docu2TeX — Word/PDF vers LaTeX")
        self.resize(920, 680)
        self.thread = None
        self.worker = None
        self._build()
        self._theme()

    def _build(self):
        root = QWidget()
        main = QVBoxLayout(root)
        main.setSpacing(14)

        header = QHBoxLayout()
        brand = QLabel("Docu2TeX")
        brand.setObjectName("brand")
        tagline = QLabel("Conversion locale • mise en page • LaTeX propre")
        tagline.setObjectName("tagline")
        header.addWidget(brand)
        header.addWidget(tagline)
        header.addStretch()
        main.addLayout(header)

        self.drop = DropZone()
        self.drop.fileDropped.connect(self.select_path)
        main.addWidget(self.drop)

        file_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Aucun fichier sélectionné")
        self.pick_btn = QPushButton("Choisir un fichier")
        self.pick_btn.clicked.connect(self.choose_file)
        file_row.addWidget(self.path_edit, 1)
        file_row.addWidget(self.pick_btn)
        main.addLayout(file_row)

        opts = QGroupBox("Options de conversion")
        opt = QVBoxLayout(opts)
        row1 = QHBoxLayout()
        self.fidelity = QComboBox()
        self.fidelity.addItem("Équilibré", "balanced")
        self.fidelity.addItem("Priorité rendu visuel", "visual")
        self.fidelity.addItem("Priorité LaTeX éditable", "editable")
        row1.addWidget(QLabel("Fidélité :"))
        row1.addWidget(self.fidelity, 1)
        row1.addWidget(QLabel("Dossier de sortie :"))
        self.output_edit = QLineEdit(str(Path.home() / "Docu2TeX"))
        row1.addWidget(self.output_edit, 2)
        self.output_btn = QPushButton("Parcourir")
        self.output_btn.clicked.connect(self.choose_output)
        row1.addWidget(self.output_btn)
        opt.addLayout(row1)

        row2 = QHBoxLayout()
        self.chk_compile = QCheckBox("Compiler le PDF")
        self.chk_compile.setChecked(True)
        self.chk_pages = QCheckBox("Préserver les sauts de page")
        self.chk_pages.setChecked(True)
        self.chk_images = QCheckBox("Préserver les images")
        self.chk_images.setChecked(True)
        self.chk_tables = QCheckBox("Optimiser les tableaux")
        self.chk_tables.setChecked(True)
        self.chk_clean = QCheckBox("Nettoyer le texte Word")
        self.chk_clean.setChecked(True)
        self.chk_pagination = QCheckBox("Ajuster la pagination")
        self.chk_pagination.setChecked(True)
        for c in (self.chk_compile, self.chk_pages, self.chk_images, self.chk_tables, self.chk_clean, self.chk_pagination):
            row2.addWidget(c)
        row2.addStretch()
        opt.addLayout(row2)
        main.addWidget(opts)

        self.convert_btn = QPushButton("CONVERTIR")
        self.convert_btn.setObjectName("convertBtn")
        self.convert_btn.clicked.connect(self.start_conversion)
        main.addWidget(self.convert_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        main.addWidget(self.progress)
        self.status = QLabel("Prêt. Les fichiers restent sur votre ordinateur.")
        self.status.setObjectName("status")
        main.addWidget(self.status)

        result_box = QGroupBox("Résultat")
        result_layout = QVBoxLayout(result_box)
        self.summary = QLabel("Aucune conversion effectuée.")
        self.summary.setWordWrap(True)
        result_layout.addWidget(self.summary)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(180)
        result_layout.addWidget(self.log)
        buttons = QHBoxLayout()
        self.open_project = QPushButton("Ouvrir le projet")
        self.open_project.setEnabled(False)
        self.open_project.clicked.connect(lambda: self._open_path(self.last_result.project_dir if self.last_result else None))
        self.open_pdf = QPushButton("Ouvrir le PDF")
        self.open_pdf.setEnabled(False)
        self.open_pdf.clicked.connect(lambda: self._open_path(self.last_result.pdf_path if self.last_result else None))
        self.open_folder = QPushButton("Ouvrir le dossier")
        self.open_folder.setEnabled(False)
        self.open_folder.clicked.connect(lambda: self._open_path(self.last_result.project_dir.parent if self.last_result and self.last_result.project_dir else None))
        buttons.addWidget(self.open_project)
        buttons.addWidget(self.open_pdf)
        buttons.addWidget(self.open_folder)
        buttons.addStretch()
        result_layout.addLayout(buttons)
        main.addWidget(result_box)

        self.last_result: ConversionResult | None = None
        self.setCentralWidget(root)

        menu = self.menuBar().addMenu("Aide")
        about = QAction("À propos", self)
        about.triggered.connect(self.show_about)
        menu.addAction(about)

    def _theme(self):
        self.setStyleSheet("""
            QWidget { background: #f5f7fb; color: #172033; }
            QGroupBox { border: 1px solid #d8deea; border-radius: 10px; margin-top: 10px; padding: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; font-weight: 700; }
            QLabel#brand { font-size: 28px; font-weight: 800; }
            QLabel#tagline { font-size: 13px; color: #667085; }
            QLabel#dropTitle { font-size: 18px; font-weight: 700; }
            QLabel#dropZone QLabel { background: transparent; }
            QFrame#dropZone { border: 2px dashed #9aa7bb; border-radius: 14px; background: #ffffff; }
            QPushButton { padding: 9px 14px; border-radius: 8px; border: 1px solid #c8d0df; background: #ffffff; }
            QPushButton:hover { background: #eef3fa; }
            QPushButton#convertBtn { font-size: 15px; font-weight: 800; padding: 12px; background: #15294b; color: white; border: none; }
            QPushButton#convertBtn:disabled { background: #aab4c3; }
            QLineEdit, QComboBox, QTextEdit { background: white; border: 1px solid #c8d0df; border-radius: 7px; padding: 7px; }
            QProgressBar { height: 12px; border: 1px solid #c8d0df; border-radius: 6px; background: white; text-align: center; }
            QProgressBar::chunk { border-radius: 5px; background: #15294b; }
            QLabel#status { color: #52607a; }
        """)

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un document", "", "Documents (*.docx *.pdf)")
        if path:
            self.select_path(path)

    def select_path(self, path: str):
        self.path_edit.setText(path)
        self.status.setText(f"Fichier : {Path(path).name}")

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie")
        if folder:
            self.output_edit.setText(folder)

    def start_conversion(self):
        source = Path(self.path_edit.text().strip())
        if not source.is_file():
            QMessageBox.warning(self, "Fichier manquant", "Sélectionnez un fichier DOCX ou PDF valide.")
            return
        out = Path(self.output_edit.text().strip() or str(Path.home() / "Docu2TeX"))
        out.mkdir(parents=True, exist_ok=True)
        options = ConversionOptions(
            output_dir=out,
            compile_pdf=self.chk_compile.isChecked(),
            fidelity=self.fidelity.currentData(),
            preserve_page_breaks=self.chk_pages.isChecked(),
            preserve_images=self.chk_images.isChecked(),
            optimize_tables=self.chk_tables.isChecked(),
            clean_text=self.chk_clean.isChecked(),
            optimize_pagination=self.chk_pagination.isChecked(),
        )
        self.convert_btn.setEnabled(False)
        self.open_project.setEnabled(False)
        self.open_pdf.setEnabled(False)
        self.open_folder.setEnabled(False)
        self.summary.setText("Conversion en cours…")
        self.log.clear()
        self.progress.setValue(0)
        self.thread = QThread()
        self.worker = Worker(source, options)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _on_progress(self, message, value):
        self.status.setText(message)
        self.progress.setValue(value)

    def _on_finished(self, result: ConversionResult):
        self.last_result = result
        self.convert_btn.setEnabled(True)
        self.open_project.setEnabled(bool(result.project_dir and result.project_dir.exists()))
        self.open_pdf.setEnabled(bool(result.pdf_path and result.pdf_path.exists()))
        self.open_folder.setEnabled(bool(result.project_dir and result.project_dir.parent.exists()))
        self.progress.setValue(100 if result.success else self.progress.value())
        if result.success:
            pages = f"{result.source_pages} → {result.output_pages}" if result.source_pages and result.output_pages else "non mesuré"
            self.summary.setText(
                f"<b>{result.status_text}</b><br>Projet : {result.project_dir}<br>Pages : {pages}<br>Images : {result.images} • Tableaux : {result.tables}<br>" +
                ("<br>".join(result.warnings) if result.warnings else "Aucun avertissement.")
            )
            self.status.setText("Prêt. Le projet a été généré hors ligne.")
            self.log.setPlainText(result.log[-9000:] if result.log else "Conversion réussie.")
        else:
            self.summary.setText("<b>Conversion échouée</b><br>" + "<br>".join(result.errors))
            self.log.setPlainText(result.log[-9000:] if result.log else "")
            QMessageBox.critical(self, "Échec de conversion", "\n".join(result.errors))

    def _open_path(self, path: Path | None):
        if not path or not path.exists():
            return
        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def show_about(self):
        QMessageBox.information(self, "Docu2TeX", "Docu2TeX V1\nConvertisseur local DOCX/PDF → LaTeX.\n\nAucune API distante n'est utilisée.")
