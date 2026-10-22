import sys
import json
import os

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QLineEdit, QPushButton, QCheckBox, QTextEdit,
    QVBoxLayout, QHBoxLayout, QComboBox, QListWidget,
    QGroupBox, QMessageBox, QRadioButton, QDialog,
    QDialogButtonBox, QFormLayout
)


TASKS_FILE = "tasks.json"


class EditTaskDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование задачи")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(task["name"])
        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(task["description"])

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText(task["priority"])

        self.important_check = QCheckBox("Важная задача")
        self.important_check.setChecked(task["important"])

        self.notification_check = QCheckBox("Уведомление")
        self.notification_check.setChecked(task["notification"])

        self.favorite_check = QCheckBox("Избранное")
        self.favorite_check.setChecked(task["favorite"])

        form.addRow("Название:", self.name_edit)
        form.addRow("Описание:", self.description_edit)
        form.addRow("Приоритет:", self.priority_combo)
        form.addRow(self.important_check)
        form.addRow(self.notification_check)
        form.addRow(self.favorite_check)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self, "Ошибка", "Название не может быть пустым."
            )
            return
        self.accept()

    def get_task(self):
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "priority": self.priority_combo.currentText(),
            "important": self.important_check.isChecked(),
            "notification": self.notification_check.isChecked(),
            "favorite": self.favorite_check.isChecked()
        }


class TaskManager(QMainWindow):
    task_created = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager 2.0")
        self.resize(700, 800)
        self.tasks = []

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.task_edit = QLineEdit()
        self.task_edit.setPlaceholderText("Название задачи")

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Описание задачи")
        self.description_edit.setMaximumHeight(90)

        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.task_edit)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.description_edit)

        priority_group = QGroupBox("Приоритет")
        priority_layout = QHBoxLayout(priority_group)

        self.low_radio = QRadioButton("Low")
        self.medium_radio = QRadioButton("Medium")
        self.high_radio = QRadioButton("High")
        self.medium_radio.setChecked(True)

        priority_layout.addWidget(self.low_radio)
        priority_layout.addWidget(self.medium_radio)
        priority_layout.addWidget(self.high_radio)
        layout.addWidget(priority_group)

        self.important_check = QCheckBox("Важная задача")
        self.notification_check = QCheckBox("Уведомление")
        self.favorite_check = QCheckBox("Избранное")

        layout.addWidget(self.important_check)
        layout.addWidget(self.notification_check)
        layout.addWidget(self.favorite_check)

        buttons = QHBoxLayout()
        self.create_button = QPushButton("Добавить задачу")
        self.clear_form_button = QPushButton("Очистить форму")
        buttons.addWidget(self.create_button)
        buttons.addWidget(self.clear_form_button)
        layout.addLayout(buttons)

        buttons2 = QHBoxLayout()
        self.delete_button = QPushButton("Удалить последнюю")
        self.delete_selected_button = QPushButton("Удалить выбранную")
        self.edit_button = QPushButton("Редактировать")
        buttons2.addWidget(self.delete_button)
        buttons2.addWidget(self.delete_selected_button)
        buttons2.addWidget(self.edit_button)
        layout.addLayout(buttons2)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Low", "Medium", "High"])
        layout.addWidget(QLabel("Фильтр по приоритету:"))
        layout.addWidget(self.filter_combo)

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        self.status_label = QLabel("Задач: 0")
        self.count_label = QLabel("Создано задач: 0")
        self.characters_label = QLabel("Название: 0 символов")
        layout.addWidget(self.status_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.characters_label)

        self.create_button.clicked.connect(self.create_task)
        self.clear_form_button.clicked.connect(self.clear_form)
        self.delete_button.clicked.connect(self.delete_last_task)
        self.delete_selected_button.clicked.connect(
            self.delete_selected_task
        )
        self.edit_button.clicked.connect(self.edit_selected_task)
        self.filter_combo.currentTextChanged.connect(self.show_tasks)
        self.task_edit.textChanged.connect(self.update_character_count)
        self.task_list.currentRowChanged.connect(self.update_buttons)
        self.task_created.connect(self.update_status)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFF0F5;
                color: #49343D;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QListWidget, QComboBox {
                background-color: white;
                border: 1px solid #E6A4B4;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #F2B6C6;
                border: none;
                border-radius: 7px;
                padding: 9px;
            }
            QPushButton:hover {
                background-color: #E991AC;
            }
            QPushButton:pressed {
                background-color: #D96F91;
            }
            QPushButton:disabled {
                background-color: #E8DDE1;
                color: #999999;
            }
            QListWidget::item:selected {
                background-color: #F6CADA;
                color: #49343D;
            }
            QGroupBox {
                border: 1px solid #E6A4B4;
                border-radius: 7px;
                margin-top: 8px;
                padding: 8px;
            }
        """)

        self.load_tasks()
        self.show_tasks()
        self.update_task_count()
        self.update_buttons(self.task_list.currentRow())

    def save_tasks(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    self.tasks, file, ensure_ascii=False, indent=4
                )
        except OSError as error:
            QMessageBox.warning(
                self, "Ошибка сохранения",
                f"Не удалось сохранить задачи:\n{error}"
            )

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            return

        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("В файле должен находиться список задач.")

            required = {
                "name", "description", "priority",
                "important", "notification", "favorite"
            }

            for task in data:
                if not isinstance(task, dict) or not required.issubset(task):
                    raise ValueError("Неверный формат задачи.")

                if task["priority"] not in ["Low", "Medium", "High"]:
                    raise ValueError("Неизвестный приоритет задачи.")

                if not isinstance(task["name"], str) or not task["name"].strip():
                    raise ValueError("У задачи отсутствует название.")

                for key in ("important", "notification", "favorite"):
                    if not isinstance(task[key], bool):
                        raise ValueError("Неверный формат параметров задачи.")

                if not isinstance(task["description"], str):
                    raise ValueError("Неверный формат описания задачи.")

            self.tasks = data

        except (OSError, json.JSONDecodeError, ValueError) as error:
            QMessageBox.warning(
                self, "Ошибка загрузки",
                f"Не удалось загрузить задачи:\n{error}"
            )

    def get_priority(self):
        if self.low_radio.isChecked():
            return "Low"
        if self.high_radio.isChecked():
            return "High"
        return "Medium"

    def create_task(self):
        name = self.task_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self, "Ошибка", "Введите название задачи."
            )
            self.task_edit.setFocus()
            return

        task = {
            "name": name,
            "description": self.description_edit.toPlainText().strip(),
            "priority": self.get_priority(),
            "important": self.important_check.isChecked(),
            "notification": self.notification_check.isChecked(),
            "favorite": self.favorite_check.isChecked()
        }

        self.tasks.append(task)
        self.save_tasks()
        self.show_tasks()
        self.update_task_count()
        self.task_created.emit()
        self.clear_form()

    def show_tasks(self):
        selected_filter = self.filter_combo.currentText()
        self.task_list.clear()

        for index, task in enumerate(self.tasks):
            if selected_filter != "All" and task["priority"] != selected_filter:
                continue

            text = f'{task["name"]} | Priority: {task["priority"]}'

            if task["important"]:
                text += " | Важная"
            if task["favorite"]:
                text += " | Избранное"

            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.task_list.addItem(item)

        self.update_buttons(self.task_list.currentRow())

    def get_selected_task_index(self):
        item = self.task_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def delete_selected_task(self):
        index = self.get_selected_task_index()
        if index is None:
            return

        answer = QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранную задачу?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.tasks.pop(index)
            self.save_tasks()
            self.show_tasks()
            self.update_task_count()
            self.update_status()

    def delete_last_task(self):
        if not self.tasks:
            QMessageBox.information(
                self, "Информация", "Список задач пуст."
            )
            return

        answer = QMessageBox.question(
            self, "Подтверждение",
            "Удалить последнюю задачу?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.tasks.pop()
            self.save_tasks()
            self.show_tasks()
            self.update_task_count()
            self.update_status()

    def edit_selected_task(self):
        index = self.get_selected_task_index()
        if index is None:
            return

        dialog = EditTaskDialog(self.tasks[index], self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.tasks[index] = dialog.get_task()
            self.save_tasks()
            self.show_tasks()
            self.update_task_count()
            self.update_status()

    def clear_form(self):
        self.task_edit.clear()
        self.description_edit.clear()
        self.low_radio.setChecked(False)
        self.medium_radio.setChecked(True)
        self.high_radio.setChecked(False)
        self.important_check.setChecked(False)
        self.notification_check.setChecked(False)
        self.favorite_check.setChecked(False)

    def update_character_count(self, text):
        self.characters_label.setText(
            f"Название: {len(text)} символов"
        )

    def update_task_count(self):
        self.count_label.setText(
            f"Всего создано задач: {len(self.tasks)}"
        )
        self.status_label.setText(f"Задач: {len(self.tasks)}")

    def update_status(self):
        self.status_label.setText(
            f"Задач: {len(self.tasks)} — список обновлён"
        )

    def update_buttons(self, row):
        selected = row >= 0
        self.delete_selected_button.setEnabled(selected)
        self.edit_button.setEnabled(selected)

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())
