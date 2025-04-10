import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar


class StudentDayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("День студента 25")
        self.root.geometry("800x600")

        # Инициализация базы данных
        self.db_file = "student_tasks.json"
        self.tasks = []
        self.events = []
        self.notes = []

        self.load_data()

        # Создание интерфейса
        self.create_widgets()

        # Обновление интерфейса
        self.update_task_list()
        self.update_event_list()
        self.update_note_list()

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = data.get("tasks", [])
                self.events = data.get("events", [])
                self.notes = data.get("notes", [])
        else:
            self.tasks = []
            self.events = []
            self.notes = []

    def save_data(self):
        """Сохранение данных в JSON файл"""
        data = {
            "tasks": self.tasks,
            "events": self.events,
            "notes": self.notes
        }
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка задач
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Задачи")
        self.create_tasks_tab()

        # Вкладка событий
        self.events_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.events_tab, text="События")
        self.create_events_tab()

        # Вкладка заметок
        self.notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.notes_tab, text="Заметки")
        self.create_notes_tab()

        # Вкладка статистики
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Статистика")
        self.create_stats_tab()

    def create_tasks_tab(self):
        """Создание вкладки задач"""
        # Панель управления задачами
        task_control_frame = ttk.Frame(self.tasks_tab)
        task_control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(task_control_frame, text="Добавить задачу", command=self.add_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_control_frame, text="Редактировать", command=self.edit_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_control_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_control_frame, text="Отметить выполненной", command=self.mark_task_completed).pack(side=tk.LEFT,
                                                                                                           padx=2)

        # Фильтры задач
        filter_frame = ttk.Frame(self.tasks_tab)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Фильтр:").pack(side=tk.LEFT)
        self.task_filter = tk.StringVar()
        self.task_filter.set("Все")

        ttk.Radiobutton(filter_frame, text="Все", variable=self.task_filter, value="Все",
                        command=self.update_task_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Активные", variable=self.task_filter, value="Активные",
                        command=self.update_task_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Завершенные", variable=self.task_filter, value="Завершенные",
                        command=self.update_task_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Высокий приоритет", variable=self.task_filter, value="Высокий",
                        command=self.update_task_list).pack(side=tk.LEFT)

        # Список задач
        self.task_list_frame = ttk.Frame(self.tasks_tab)
        self.task_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "title", "priority", "due_date", "completed")
        self.task_tree = ttk.Treeview(self.task_list_frame, columns=columns, show="headings", selectmode="browse")

        self.task_tree.heading("id", text="ID")
        self.task_tree.heading("title", text="Название")
        self.task_tree.heading("priority", text="Приоритет")
        self.task_tree.heading("due_date", text="Срок")
        self.task_tree.heading("completed", text="Статус")

        self.task_tree.column("id", width=50, anchor=tk.CENTER)
        self.task_tree.column("title", width=200)
        self.task_tree.column("priority", width=100, anchor=tk.CENTER)
        self.task_tree.column("due_date", width=100, anchor=tk.CENTER)
        self.task_tree.column("completed", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.task_list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Поиск задач
        search_frame = ttk.Frame(self.tasks_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.task_search_var = tk.StringVar()
        self.task_search_var.trace("w", lambda *args: self.update_task_list())
        ttk.Entry(search_frame, textvariable=self.task_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def create_events_tab(self):
        """Создание вкладки событий"""
        # Панель управления событиями
        event_control_frame = ttk.Frame(self.events_tab)
        event_control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(event_control_frame, text="Добавить событие", command=self.add_event_dialog).pack(side=tk.LEFT,
                                                                                                     padx=2)
        ttk.Button(event_control_frame, text="Редактировать", command=self.edit_event).pack(side=tk.LEFT, padx=2)
        ttk.Button(event_control_frame, text="Удалить", command=self.delete_event).pack(side=tk.LEFT, padx=2)

        # Фильтры событий
        filter_frame = ttk.Frame(self.events_tab)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Фильтр:").pack(side=tk.LEFT)
        self.event_filter = tk.StringVar()
        self.event_filter.set("Все")

        ttk.Radiobutton(filter_frame, text="Все", variable=self.event_filter, value="Все",
                        command=self.update_event_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Предстоящие", variable=self.event_filter, value="Предстоящие",
                        command=self.update_event_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Прошедшие", variable=self.event_filter, value="Прошедшие",
                        command=self.update_event_list).pack(side=tk.LEFT)

        # Список событий
        self.event_list_frame = ttk.Frame(self.events_tab)
        self.event_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "title", "date", "time", "reminder")
        self.event_tree = ttk.Treeview(self.event_list_frame, columns=columns, show="headings", selectmode="browse")

        self.event_tree.heading("id", text="ID")
        self.event_tree.heading("title", text="Название")
        self.event_tree.heading("date", text="Дата")
        self.event_tree.heading("time", text="Время")
        self.event_tree.heading("reminder", text="Напоминание")

        self.event_tree.column("id", width=50, anchor=tk.CENTER)
        self.event_tree.column("title", width=200)
        self.event_tree.column("date", width=100, anchor=tk.CENTER)
        self.event_tree.column("time", width=100, anchor=tk.CENTER)
        self.event_tree.column("reminder", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.event_list_frame, orient=tk.VERTICAL, command=self.event_tree.yview)
        self.event_tree.configure(yscroll=scrollbar.set)

        self.event_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Поиск событий
        search_frame = ttk.Frame(self.events_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.event_search_var = tk.StringVar()
        self.event_search_var.trace("w", lambda *args: self.update_event_list())
        ttk.Entry(search_frame, textvariable=self.event_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def create_notes_tab(self):
        """Создание вкладки заметок"""
        # Панель управления заметками
        note_control_frame = ttk.Frame(self.notes_tab)
        note_control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(note_control_frame, text="Добавить заметку", command=self.add_note_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(note_control_frame, text="Редактировать", command=self.edit_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(note_control_frame, text="Удалить", command=self.delete_note).pack(side=tk.LEFT, padx=2)

        # Список заметок
        self.note_list_frame = ttk.Frame(self.notes_tab)
        self.note_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "title", "created", "updated")
        self.note_tree = ttk.Treeview(self.note_list_frame, columns=columns, show="headings", selectmode="browse")

        self.note_tree.heading("id", text="ID")
        self.note_tree.heading("title", text="Название")
        self.note_tree.heading("created", text="Создана")
        self.note_tree.heading("updated", text="Изменена")

        self.note_tree.column("id", width=50, anchor=tk.CENTER)
        self.note_tree.column("title", width=200)
        self.note_tree.column("created", width=150, anchor=tk.CENTER)
        self.note_tree.column("updated", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.note_list_frame, orient=tk.VERTICAL, command=self.note_tree.yview)
        self.note_tree.configure(yscroll=scrollbar.set)

        self.note_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Поиск заметок
        search_frame = ttk.Frame(self.notes_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.note_search_var = tk.StringVar()
        self.note_search_var.trace("w", lambda *args: self.update_note_list())
        ttk.Entry(search_frame, textvariable=self.note_search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def create_stats_tab(self):
        """Создание вкладки статистики"""
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Статистика по задачам
        ttk.Label(stats_frame, text="Статистика задач", font=("Arial", 12, "bold")).pack(pady=5)

        task_stats_frame = ttk.Frame(stats_frame)
        task_stats_frame.pack(fill=tk.X, pady=5)

        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.get("completed", False)])
        active_tasks = total_tasks - completed_tasks
        high_priority = len([t for t in self.tasks if t.get("priority", "Средний") == "Высокий"])

        ttk.Label(task_stats_frame, text=f"Всего задач: {total_tasks}").pack(anchor=tk.W)
        ttk.Label(task_stats_frame, text=f"Завершено: {completed_tasks}").pack(anchor=tk.W)
        ttk.Label(task_stats_frame, text=f"Активных: {active_tasks}").pack(anchor=tk.W)
        ttk.Label(task_stats_frame, text=f"Высокий приоритет: {high_priority}").pack(anchor=tk.W)

        # Статистика по событиям
        ttk.Label(stats_frame, text="\nСтатистика событий", font=("Arial", 12, "bold")).pack(pady=5)

        event_stats_frame = ttk.Frame(stats_frame)
        event_stats_frame.pack(fill=tk.X, pady=5)

        total_events = len(self.events)
        today = datetime.now().date()
        upcoming_events = len([e for e in self.events if datetime.strptime(e["date"], "%Y-%m-%d").date() >= today])
        past_events = total_events - upcoming_events

        ttk.Label(event_stats_frame, text=f"Всего событий: {total_events}").pack(anchor=tk.W)
        ttk.Label(event_stats_frame, text=f"Предстоящие: {upcoming_events}").pack(anchor=tk.W)
        ttk.Label(event_stats_frame, text=f"Прошедшие: {past_events}").pack(anchor=tk.W)

        # Статистика по заметкам
        ttk.Label(stats_frame, text="\nСтатистика заметок", font=("Arial", 12, "bold")).pack(pady=5)

        note_stats_frame = ttk.Frame(stats_frame)
        note_stats_frame.pack(fill=tk.X, pady=5)

        total_notes = len(self.notes)

        ttk.Label(note_stats_frame, text=f"Всего заметок: {total_notes}").pack(anchor=tk.W)

    # Методы для работы с задачами
    def add_task_dialog(self):
        """Диалог добавления новой задачи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название задачи:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Описание:").pack()
        desc_entry = tk.Text(dialog, height=5)
        desc_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Приоритет:").pack()
        priority_var = tk.StringVar(value="Средний")
        ttk.Combobox(dialog, textvariable=priority_var, values=["Низкий", "Средний", "Высокий"]).pack(fill=tk.X,
                                                                                                      padx=10, pady=5)

        ttk.Label(dialog, text="Срок выполнения (ГГГГ-ММ-ДД):").pack()
        due_entry = ttk.Entry(dialog)
        due_entry.pack(fill=tk.X, padx=10, pady=5)

        def save_task():
            title = title_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            priority = priority_var.get()
            due_date = due_entry.get().strip()

            if not title:
                messagebox.showerror("Ошибка", "Название задачи обязательно!")
                return

            try:
                if due_date:
                    datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return

            task_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1
            new_task = {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date if due_date else None,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.tasks.append(new_task)
            self.save_data()
            self.update_task_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_task).pack(pady=10)

    def edit_task(self):
        """Редактирование выбранной задачи"""
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return

        item = self.task_tree.item(selected)
        task_id = int(item["values"][0])
        task = next((t for t in self.tasks if t["id"] == task_id), None)

        if not task:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать задачу")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название задачи:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, task["title"])
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Описание:").pack()
        desc_entry = tk.Text(dialog, height=5)
        desc_entry.insert("1.0", task.get("description", ""))
        desc_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Приоритет:").pack()
        priority_var = tk.StringVar(value=task.get("priority", "Средний"))
        ttk.Combobox(dialog, textvariable=priority_var, values=["Низкий", "Средний", "Высокий"]).pack(fill=tk.X,
                                                                                                      padx=10, pady=5)

        ttk.Label(dialog, text="Срок выполнения (ГГГГ-ММ-ДД):").pack()
        due_entry = ttk.Entry(dialog)
        due_entry.insert(0, task.get("due_date", ""))
        due_entry.pack(fill=tk.X, padx=10, pady=5)

        completed_var = tk.BooleanVar(value=task.get("completed", False))
        ttk.Checkbutton(dialog, text="Завершено", variable=completed_var).pack()

        def save_changes():
            title = title_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            priority = priority_var.get()
            due_date = due_entry.get().strip()
            completed = completed_var.get()

            if not title:
                messagebox.showerror("Ошибка", "Название задачи обязательно!")
                return

            try:
                if due_date:
                    datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return

            task["title"] = title
            task["description"] = description
            task["priority"] = priority
            task["due_date"] = due_date if due_date else None
            task["completed"] = completed
            task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.save_data()
            self.update_task_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=10)

    def delete_task(self):
        """Удаление выбранной задачи"""
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return

        item = self.task_tree.item(selected)
        task_id = int(item["values"][0])

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_data()
            self.update_task_list()

    def mark_task_completed(self):
        """Отметка задачи как выполненной"""
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для отметки")
            return

        item = self.task_tree.item(selected)
        task_id = int(item["values"][0])
        task = next((t for t in self.tasks if t["id"] == task_id), None)

        if task:
            task["completed"] = True
            task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_data()
            self.update_task_list()

    def update_task_list(self):
        """Обновление списка задач"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        search_text = self.task_search_var.get().lower()
        filter_type = self.task_filter.get()

        for task in sorted(self.tasks, key=lambda x: x.get("due_date", "9999-99-99")):
            # Применение фильтра
            if filter_type == "Активные" and task.get("completed", False):
                continue
            if filter_type == "Завершенные" and not task.get("completed", False):
                continue
            if filter_type == "Высокий" and task.get("priority", "") != "Высокий":
                continue

            # Применение поиска
            task_text = (task["title"] + " " + task.get("description", "")).lower()
            if search_text and search_text not in task_text:
                continue

            due_date = task.get("due_date", "")
            status = "Завершено" if task.get("completed", False) else "Активно"

            self.task_tree.insert("", tk.END, values=(
                task["id"],
                task["title"],
                task.get("priority", "Средний"),
                due_date if due_date else "Нет срока",
                status
            ))

    # Методы для работы с событиями
    def add_event_dialog(self):
        """Диалог добавления нового события"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить событие")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название события:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Описание:").pack()
        desc_entry = tk.Text(dialog, height=5)
        desc_entry.pack(fill=tk.X, padx=10, pady=5)

        # Календарь для выбора даты
        ttk.Label(dialog, text="Дата события:").pack()
        cal_frame = ttk.Frame(dialog)
        cal_frame.pack(pady=5)
        cal = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack()

        ttk.Label(dialog, text="Время (ЧЧ:ММ):").pack()
        time_entry = ttk.Entry(dialog)
        time_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Напоминание (минуты до события):").pack()
        reminder_entry = ttk.Entry(dialog)
        reminder_entry.pack(fill=tk.X, padx=10, pady=5)

        def save_event():
            title = title_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            date = cal.get_date()
            time = time_entry.get().strip()
            reminder = reminder_entry.get().strip()

            if not title:
                messagebox.showerror("Ошибка", "Название события обязательно!")
                return

            try:
                datetime.strptime(date, "%Y-%m-%d")
                if time:
                    datetime.strptime(time, "%H:%M")
                if reminder:
                    int(reminder)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат данных!")
                return

            event_id = max([e.get("id", 0) for e in self.events], default=0) + 1
            new_event = {
                "id": event_id,
                "title": title,
                "description": description,
                "date": date,
                "time": time if time else None,
                "reminder": int(reminder) if reminder else None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.events.append(new_event)
            self.save_data()
            self.update_event_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_event).pack(pady=10)

    def edit_event(self):
        """Редактирование выбранного события"""
        selected = self.event_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите событие для редактирования")
            return

        item = self.event_tree.item(selected)
        event_id = int(item["values"][0])
        event = next((e for e in self.events if e["id"] == event_id), None)

        if not event:
            messagebox.showerror("Ошибка", "Событие не найдено")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать событие")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название события:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, event["title"])
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Описание:").pack()
        desc_entry = tk.Text(dialog, height=5)
        desc_entry.insert("1.0", event.get("description", ""))
        desc_entry.pack(fill=tk.X, padx=10, pady=5)

        # Календарь для выбора даты
        ttk.Label(dialog, text="Дата события:").pack()
        cal_frame = ttk.Frame(dialog)
        cal_frame.pack(pady=5)
        cal = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.set_date(event["date"])
        cal.pack()

        ttk.Label(dialog, text="Время (ЧЧ:ММ):").pack()
        time_entry = ttk.Entry(dialog)
        time_entry.insert(0, event.get("time", ""))
        time_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Напоминание (минуты до события):").pack()
        reminder_entry = ttk.Entry(dialog)
        reminder_entry.insert(0, str(event.get("reminder", "")) if event.get("reminder") else "")
        reminder_entry.pack(fill=tk.X, padx=10, pady=5)

        def save_changes():
            title = title_entry.get().strip()
            description = desc_entry.get("1.0", tk.END).strip()
            date = cal.get_date()
            time = time_entry.get().strip()
            reminder = reminder_entry.get().strip()

            if not title:
                messagebox.showerror("Ошибка", "Название события обязательно!")
                return

            try:
                datetime.strptime(date, "%Y-%m-%d")
                if time:
                    datetime.strptime(time, "%H:%M")
                if reminder:
                    int(reminder)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат данных!")
                return

            event["title"] = title
            event["description"] = description
            event["date"] = date
            event["time"] = time if time else None
            event["reminder"] = int(reminder) if reminder else None
            event["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.save_data()
            self.update_event_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=10)

    def delete_event(self):
        """Удаление выбранного события"""
        selected = self.event_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите событие для удаления")
            return

        item = self.event_tree.item(selected)
        event_id = int(item["values"][0])

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это событие?"):
            self.events = [e for e in self.events if e["id"] != event_id]
            self.save_data()
            self.update_event_list()

    def update_event_list(self):
        """Обновление списка событий"""
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)

        search_text = self.event_search_var.get().lower()
        filter_type = self.event_filter.get()
        today = datetime.now().date()

        for event in sorted(self.events, key=lambda x: (x["date"], x.get("time", "00:00"))):
            # Применение фильтра
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if filter_type == "Предстоящие" and event_date < today:
                continue
            if filter_type == "Прошедшие" and event_date >= today:
                continue

            # Применение поиска
            event_text = (event["title"] + " " + event.get("description", "")).lower()
            if search_text and search_text not in event_text:
                continue

            self.event_tree.insert("", tk.END, values=(
                event["id"],
                event["title"],
                event["date"],
                event.get("time", "Весь день"),
                f"{event.get('reminder', 'Нет')} мин" if event.get("reminder") else "Нет"
            ))

    # Методы для работы с заметками
    def add_note_dialog(self):
        """Диалог добавления новой заметки"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить заметку")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название заметки:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Содержание:").pack()
        content_entry = tk.Text(dialog, height=15)
        content_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def save_note():
            title = title_entry.get().strip()
            content = content_entry.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Ошибка", "Название заметки обязательно!")
                return

            note_id = max([n.get("id", 0) for n in self.notes], default=0) + 1
            new_note = {
                "id": note_id,
                "title": title,
                "content": content,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.notes.append(new_note)
            self.save_data()
            self.update_note_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_note).pack(pady=10)

    def edit_note(self):
        """Редактирование выбранной заметки"""
        selected = self.note_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заметку для редактирования")
            return

        item = self.note_tree.item(selected)
        note_id = int(item["values"][0])
        note = next((n for n in self.notes if n["id"] == note_id), None)

        if not note:
            messagebox.showerror("Ошибка", "Заметка не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать заметку")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название заметки:").pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, note["title"])
        title_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="Содержание:").pack()
        content_entry = tk.Text(dialog, height=15)
        content_entry.insert("1.0", note["content"])
        content_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def save_changes():
            title = title_entry.get().strip()
            content = content_entry.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Ошибка", "Название заметки обязательно!")
                return

            note["title"] = title
            note["content"] = content
            note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.save_data()
            self.update_note_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=10)

    def delete_note(self):
        """Удаление выбранной заметки"""
        selected = self.note_tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заметку для удаления")
            return

        item = self.note_tree.item(selected)
        note_id = int(item["values"][0])

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту заметку?"):
            self.notes = [n for n in self.notes if n["id"] != note_id]
            self.save_data()
            self.update_note_list()

    def update_note_list(self):
        """Обновление списка заметок"""
        for item in self.note_tree.get_children():
            self.note_tree.delete(item)

        search_text = self.note_search_var.get().lower()

        for note in sorted(self.notes, key=lambda x: x["updated_at"], reverse=True):
            # Применение поиска
            note_text = (note["title"] + " " + note["content"]).lower()
            if search_text and search_text not in note_text:
                continue

            created = datetime.strptime(note["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
            updated = datetime.strptime(note["updated_at"], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")

            self.note_tree.insert("", tk.END, values=(
                note["id"],
                note["title"],
                created,
                updated
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentDayApp(root)
    root.mainloop()