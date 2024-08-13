import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QMessageBox,
    QListWidget,
    QProgressBar,
)
from PyPDF2 import PdfMerger

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesclar PDF")
        self.setGeometry(100, 100, 600, 400)

        self.select_button = QPushButton("Selecione os arquivos PDFs")
        self.select_button.clicked.connect(self.select_files)

        self.remove_button = QPushButton("Remover arquivo selecionado")
        self.remove_button.clicked.connect(self.remove_file)
        self.remove_button.setEnabled(False)

        self.merge_button = QPushButton("Mesclar PDFs")
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.merge_button.setEnabled(False)  # Disable until files are selected

        self.status_label = QLabel("")
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.update_remove_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.file_list)
        layout.addWidget(self.merge_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.selected_files = []

    def select_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Arquivos PDFs (*.pdf)")
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if all(file.endswith('.pdf') for file in files):
                self.selected_files.extend(files)
                self.file_list.addItems(files)
                self.merge_button.setEnabled(True)
                self.status_label.setText(f"{len(self.selected_files)} arquivos selecionados.")
                logging.info(f"Arquivos selecionados: {self.selected_files}")
            else:
                QMessageBox.warning(self, "Formato inválido", "Por favor selecione apenas arquivos PDFs.")
                logging.warning("Formato inválido selecionado.")

    def remove_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_files.remove(item.text())
            self.file_list.takeItem(self.file_list.row(item))
        self.status_label.setText(f"{len(self.selected_files)} arquivos selecionados.")
        if not self.selected_files:
            self.merge_button.setEnabled(False)
        logging.info(f"Arquivos removidos: {[item.text() for item in selected_items]}")

    def update_remove_button(self):
        self.remove_button.setEnabled(bool(self.file_list.selectedItems()))

    def merge_pdfs(self):
        if not self.selected_files:
            QMessageBox.warning(self, "Nenhum arquivo selecionado", "Por favor selecione os arquivos PDFs.")
            return

        try:
            merger = PdfMerger()
            # Sort files alphabetically
            self.selected_files.sort()
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.selected_files))
            for i, pdf in enumerate(self.selected_files):
                merger.append(pdf)
                self.progress_bar.setValue(i + 1)

            save_dialog = QFileDialog()
            save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            save_dialog.setNameFilter("Arquivos PDFs (*.pdf)")
            if save_dialog.exec():
                output_filename = save_dialog.selectedFiles()[0]
                merger.write(output_filename)
                merger.close()
                self.status_label.setText(f"PDFs mesclados com sucesso para {output_filename}")
                logging.info(f"PDFs mesclados para {output_filename}")
                QMessageBox.information(self, "Sucesso", "PDFs mesclados com sucesso!")
                self.open_pdf(output_filename)

        except Exception as e:
            logging.error(f"Erro durante a mesclagem: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante a mesclagem: {e}")
        finally:
            self.progress_bar.setVisible(False)

    def open_pdf(self, filename):
        try:
            if sys.platform == "win32":
                os.startfile(filename)
            else:
                os.system(f"open {filename}")
        except Exception as e:
            logging.error(f"Erro ao abrir o PDF: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao abrir o PDF: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())