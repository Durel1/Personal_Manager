"""Single-window CustomTkinter preview, with background database operations."""
import math
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from tkinter import StringVar, TclError, filedialog, messagebox, ttk

import customtkinter as ctk

from backend.auth import AuthenticationError, authenticate_user, register_user
from backend.dashboard import FILTER_OPTIONS, MODULES, list_records, user_profile
from backend.migrations import MigrationError, migrate_application
from backend.permissions import ROLE_LABELS, allowed, current_user, list_users, set_role
from backend.alerts import alerts_snapshot, record_alert
from backend.reporting import export_report
from backend.management import delete_record, form_fields, get_record, initial_values, save_record
from backend.statistics import statistics_snapshot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.charts import event_figure, spending_figure

BACKGROUND = ('#F3F6FB', '#0B1220')
SURFACE = ('#FFFFFF', '#142033')
MUTED = ('#52647B', '#9CADC2')
TEXT = ('#17283F', '#EDF3FB')
ACCENT = '#0F8C9F'
HOVER = '#0C7383'
FONT = 'Segoe UI'


class PersonalManager(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode('Dark')
        super().__init__()
        self.title('PersonalManager')
        self.geometry('1180x760')
        self.minsize(1000, 680)
        self.configure(fg_color=BACKGROUND)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.generation = 0
        self.polls = set()
        self.user = None
        self.chart_canvases = []
        self.current_view = None
        self.list_filters = {}
        self.search_timer = None
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.apply_table_theme()
        self.replace_root()
        loading = ctk.CTkFrame(self.screen, fg_color='transparent')
        loading.place(relx=0.5, rely=0.5, anchor='center')
        self.label(loading, 'PersonalManager', size=30, bold=True).pack(pady=12)
        self.label(loading, 'Préparation de votre espace…', muted=True).pack()
        progress = ctk.CTkProgressBar(loading, width=300, mode='indeterminate', progress_color=ACCENT)
        progress.pack(pady=24)
        progress.start()
        self.run_task(migrate_application, lambda _: self.show_login(), fatal=True)

    def label(self, master, text, size=14, bold=False, muted=False, **kwargs):
        return ctk.CTkLabel(master, text=text, text_color=MUTED if muted else TEXT,
                            font=(FONT, size, 'bold' if bold else 'normal'), **kwargs)

    def button(self, master, text, command, secondary=False, **kwargs):
        return ctk.CTkButton(master, text=text, command=command, height=42,
                             corner_radius=9, font=(FONT, 14),
                             fg_color=SURFACE if secondary else ACCENT,
                             hover_color=('#E7EDF5', '#21334B') if secondary else HOVER,
                             text_color=TEXT if secondary else '#FFFFFF', **kwargs)

    def replace_root(self):
        self.cancel_search()
        self.cleanup_charts()
        self.generation += 1
        for widget in self.winfo_children():
            widget.destroy()
        self.screen = ctk.CTkFrame(self, fg_color=BACKGROUND, corner_radius=0)
        self.screen.grid(row=0, column=0, sticky='nsew')

    def clear_content(self):
        self.cancel_search()
        self.cleanup_charts()
        self.generation += 1
        for widget in self.content.winfo_children():
            widget.destroy()
        self.content.grid_rowconfigure(1, weight=0)

    def run_task(self, action, success, button=None, error_label=None, fatal=False, error_callback=None):
        """Only the main Tk thread touches widgets; the worker handles SQLite/bcrypt."""
        generation = self.generation
        if button is not None:
            button.configure(state='disabled')
        future = self.executor.submit(action)

        def poll():
            self.polls.discard(poll_id[0])
            if not future.done():
                poll_id[0] = self.after(50, poll)
                self.polls.add(poll_id[0])
                return
            if generation != self.generation:
                return  # A navigation invalidated this result.
            if button is not None:
                button.configure(state='normal')
            try:
                result = future.result()
            except (AuthenticationError, MigrationError, ValueError) as error:
                report(str(error))
            except sqlite3.Error:
                report('La base de données est indisponible. Réessayez.')
            except Exception:
                report('Une erreur inattendue est survenue. Fermez puis relancez l’application.')
            else:
                success(result)

        def report(text):
            if error_callback is not None:
                error_callback(text)
            elif error_label is not None:
                error_label.configure(text=text)
            else:
                messagebox.showerror('PersonalManager', text, parent=self)
            if fatal:
                self.close()

        poll_id = [self.after(50, poll)]
        self.polls.add(poll_id[0])

    def close(self):
        self.cancel_search()
        self.cleanup_charts()
        for identifier in self.polls:
            self.after_cancel(identifier)
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()

    def auth_layout(self, title, subtitle):
        self.replace_root()
        self.screen.grid_columnconfigure((0, 1), weight=1, uniform='auth')
        self.screen.grid_rowconfigure(0, weight=1)
        brand = ctk.CTkFrame(self.screen, fg_color='#102239', corner_radius=0)
        brand.grid(row=0, column=0, sticky='nsew')
        body = ctk.CTkFrame(brand, fg_color='transparent')
        body.place(relx=0.5, rely=0.5, anchor='center')
        ctk.CTkLabel(body, text='PM / PersonalManager', text_color='#67D4DE',
                     font=(FONT, 18, 'bold')).pack(anchor='w', pady=(0, 30))
        ctk.CTkLabel(body, text='Votre activité.\nUne vision claire.', justify='left',
                     text_color='#FFFFFF', font=(FONT, 34, 'bold')).pack(anchor='w')
        ctk.CTkLabel(body, text='Retrouvez vos équipes, vos clients et vos\nrendez-vous dans un même espace.',
                     justify='left', text_color='#AABBD0', font=(FONT, 15)).pack(anchor='w', pady=24)
        for text in ('Équipes et contacts', 'Agenda et suivi financier', 'Données conservées localement'):
            ctk.CTkLabel(body, text='—  '+text, text_color='#DDE6F2', font=(FONT, 14)).pack(anchor='w', pady=7)
        area = ctk.CTkFrame(self.screen, fg_color='transparent')
        area.grid(row=0, column=1, sticky='nsew', padx=40, pady=25)
        card = ctk.CTkFrame(area, fg_color=SURFACE, corner_radius=18, width=400)
        card.pack(expand=True, fill='x')
        self.label(card, title, size=26, bold=True).pack(anchor='w', padx=28, pady=(25, 6))
        self.label(card, subtitle, muted=True).pack(anchor='w', padx=28, pady=(0, 15))
        return card

    def field(self, master, name, secret=False):
        self.label(master, name, size=13).pack(anchor='w', padx=28, pady=(9, 5))
        entry = ctk.CTkEntry(master, height=40, corner_radius=8, font=(FONT, 14),
                              show='*' if secret else '')
        entry.pack(fill='x', padx=28)
        return entry

    def show_login(self, notice=''):
        self.list_filters.clear()
        self.user = None
        card = self.auth_layout('Bienvenue', 'Connectez-vous à votre espace de travail.')
        name = self.field(card, 'Nom utilisateur')
        password = self.field(card, 'Mot de passe', secret=True)
        error = self.label(card, notice, size=12, wraplength=330)
        error.configure(text_color=('#B42318', '#FF9D97'))
        error.pack(fill='x', padx=28, pady=10)

        def submit():
            username, secret = name.get().strip(), password.get()
            if not username or not secret:
                error.configure(text='Veuillez remplir tous les champs.')
                return
            error.configure(text='Connexion en cours…')
            self.run_task(lambda: authenticate_user(username, secret), logged_in,
                          button=login, error_label=error)

        def logged_in(user):
            if user is None:
                error.configure(text='Nom utilisateur ou mot de passe incorrect.')
                return
            self.user = user
            self.show_shell()

        login = self.button(card, 'Se connecter', submit)
        login.pack(fill='x', padx=28, pady=(0, 10))
        self.button(card, 'Créer un compte', self.show_register, secondary=True).pack(fill='x', padx=28)
        self.button(card, 'Mot de passe oublié ?', lambda: messagebox.showinfo(
            'Mot de passe', 'La réinitialisation sécurisée n’est pas encore disponible.', parent=self),
            secondary=True).pack(fill='x', padx=28, pady=(8, 24))
        password.bind('<Return>', lambda _: submit() if login.cget('state') != 'disabled' else None)
        name.focus_set()

    def show_register(self):
        card = self.auth_layout('Créer un compte', 'Vos informations restent sur cet ordinateur.')
        fields = {key: self.field(card, title, secret=(key == 'password')) for key, title in
                  (('fullname', 'Nom utilisateur'), ('email', 'E-mail'), ('phone', 'Téléphone'),
                   ('password', 'Mot de passe · 8 caractères minimum'))}
        gender = ctk.CTkOptionMenu(card, values=['Homme', 'Femme'], height=36, font=(FONT, 14),
                                   fg_color=ACCENT, button_color=HOVER)
        gender.pack(fill='x', padx=28, pady=12)
        error = self.label(card, '', size=12, wraplength=330)
        error.configure(text_color=('#B42318', '#FF9D97'))
        error.pack(fill='x', padx=28, pady=4)

        def submit():
            values = {key: entry.get() for key, entry in fields.items()}
            selected_gender = gender.get()
            error.configure(text='Création du compte…')
            self.run_task(lambda: register_user(values['fullname'], values['password'],
                          values['email'], values['phone'], selected_gender),
                          lambda _: self.show_login('Compte créé. Vous pouvez vous connecter.'),
                          button=save, error_label=error)

        save = self.button(card, 'Créer mon compte', submit)
        save.pack(fill='x', padx=28, pady=8)
        self.button(card, 'Retour à la connexion', self.show_login, secondary=True).pack(
            fill='x', padx=28, pady=(0, 22))

    def show_shell(self):
        identifier = self.user['id']
        self.run_task(lambda: current_user(identifier), self.build_shell)

    def build_shell(self, user):
        self.user = user
        self.replace_root()
        self.screen.grid_rowconfigure(0, weight=1)
        self.screen.grid_columnconfigure(1, weight=1)
        sidebar = ctk.CTkFrame(self.screen, width=220, fg_color='#102239', corner_radius=0)
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(10, weight=1)
        ctk.CTkLabel(sidebar, text='PM / PersonalManager', text_color='#67D4DE',
                     font=(FONT, 16, 'bold')).grid(row=0, column=0, padx=20, pady=(30, 8), sticky='w')
        ctk.CTkLabel(sidebar, text=self.user['fullname']+' · '+ROLE_LABELS[self.user['role']], text_color='#AABBD0',
                     font=(FONT, 13), wraplength=175).grid(row=1, column=0, padx=20, pady=(0, 28), sticky='w')
        self.navigation = {}
        for row, (key, title) in enumerate([('home', 'Vue d’ensemble')]+
                                           [(key, module.title) for key, module in MODULES.items()
                                            if allowed(self.user['role'], key)]+
                                           [('profile', 'Mon compte')]+
                                           ([('users', 'Permissions')] if self.user['role'] == 'admin' else []), 2):
            button = ctk.CTkButton(sidebar, text=title, anchor='w', height=44,
                                   font=(FONT, 14), corner_radius=8, fg_color='transparent',
                                   hover_color='#203B55', command=lambda key=key: self.navigate(key))
            button.grid(row=row, column=0, sticky='ew', padx=14, pady=4)
            self.navigation[key] = button
        theme_menu = ctk.CTkOptionMenu(sidebar, values=['Sombre', 'Clair'], command=self.change_theme,
                          fg_color='#203B55', button_color='#2B4C67', font=(FONT, 13))
        theme_menu.set('Clair' if ctk.get_appearance_mode() == 'Light' else 'Sombre')
        theme_menu.grid(row=11, column=0, padx=18, pady=10, sticky='ew')
        self.button(sidebar, 'Se déconnecter', self.show_login).grid(row=12, column=0,
                                                                  padx=18, pady=(5, 25), sticky='ew')
        self.content = ctk.CTkFrame(self.screen, fg_color='transparent')
        self.content.grid(row=0, column=1, sticky='nsew', padx=30, pady=28)
        self.content.grid_columnconfigure(0, weight=1)
        self.navigate('home')

    def change_theme(self, selection):
        ctk.set_appearance_mode('Light' if selection == 'Clair' else 'Dark')
        self.apply_table_theme()
        if self.current_view == 'home':
            self.navigate('home')

    def apply_table_theme(self):
        dark = ctk.get_appearance_mode() == 'Dark'
        background, foreground = ('#142033', '#EDF3FB') if dark else ('#FFFFFF', '#17283F')
        heading = '#20334C' if dark else '#E7EEF6'
        self.style.configure('PM.Treeview', background=background, fieldbackground=background,
                             foreground=foreground, rowheight=38, borderwidth=0, font=(FONT, 12))
        self.style.configure('PM.Treeview.Heading', background=heading, foreground=foreground,
                             font=(FONT, 12, 'bold'), padding=12, relief='flat')
        self.style.map('PM.Treeview', background=[('selected', ACCENT)], foreground=[('selected', 'white')])
        self.style.map('PM.Treeview.Heading', background=[('active', heading)])
        if hasattr(self, 'record_tree') and self.record_tree.winfo_exists():
            self.apply_alert_theme(self.record_tree)

    def apply_alert_theme(self, tree):
        dark = ctk.get_appearance_mode() == 'Dark'
        tree.tag_configure('today', background='#443817' if dark else '#FFF3CE',
                           foreground='#FFE49A' if dark else '#754C00')
        tree.tag_configure('overdue', background='#4A222B' if dark else '#FEE5E5',
                           foreground='#FFC1C1' if dark else '#912018')

    def navigate(self, key, page=0, notice=''):
        if self.user is None or not allowed(self.user.get('role'), key):
            messagebox.showerror('Accès refusé', 'Votre rôle ne permet pas cette page.', parent=self)
            return
        self.current_view = key
        self.clear_content()
        for name, button in self.navigation.items():
            button.configure(fg_color=ACCENT if name == key else 'transparent')
        if key == 'home':
            self.home()
        elif key == 'profile':
            self.profile()
        elif key == 'users':
            self.users()
        else:
            self.records(key, page, notice)

    def heading(self, title, subtitle, refresh, action_label='Actualiser'):
        bar = ctk.CTkFrame(self.content, fg_color='transparent')
        bar.grid(row=0, column=0, sticky='ew', pady=(0, 24))
        bar.grid_columnconfigure(0, weight=1)
        self.label(bar, title, size=28, bold=True).grid(row=0, column=0, sticky='w')
        self.label(bar, subtitle, muted=True).grid(row=1, column=0, sticky='w', pady=5)
        self.button(bar, action_label, refresh, secondary=True, width=110).grid(row=0, column=1, rowspan=2, padx=(10, 0))

    def cancel_search(self):
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)
            self.search_timer = None

    def cleanup_charts(self):
        for canvas in self.chart_canvases:
            # TkAgg schedules resize/idle callbacks on its widget; cancel before destroying it.
            widget = canvas.get_tk_widget()
            for attribute in ('_idle_draw_id', '_event_loop_id'):
                identifier = getattr(canvas, attribute, None)
                if identifier is not None:
                    try:
                        widget.after_cancel(identifier)
                    except TclError:
                        pass
                    setattr(canvas, attribute, None)
            canvas.figure.clear()
        self.chart_canvases.clear()

    def mount_chart(self, parent, figure):
        canvas = FigureCanvasTkAgg(figure, master=parent)
        self.chart_canvases.append(canvas)
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=(0, 12))
        canvas.draw()

    def home(self):
        self.heading('Vue d’ensemble', date.today().strftime('%d/%m/%Y')+' · Votre activité en un coup d’œil',
                     lambda: self.navigate('home'))
        self.content.grid_rowconfigure(1, weight=1)
        body = ctk.CTkScrollableFrame(self.content, fg_color='transparent')
        body.grid(row=1, column=0, sticky='nsew')
        body.grid_columnconfigure(0, weight=1)
        cards = ctk.CTkFrame(body, fg_color='transparent')
        cards.grid(row=0, column=0, sticky='ew')
        numbers = {}
        visible_modules = [(key, module) for key, module in MODULES.items() if allowed(self.user['role'], key)]
        cards.grid_columnconfigure(tuple(range(len(visible_modules))), weight=1, uniform='cards')
        for index, (key, module) in enumerate(visible_modules):
            card = ctk.CTkFrame(cards, fg_color=SURFACE, corner_radius=12)
            card.grid(row=0, column=index, sticky='ew', padx=(0, 8), pady=(0, 14))
            self.label(card, module.title, size=12, muted=True).pack(anchor='w', padx=14, pady=(14, 0))
            numbers[key] = self.label(card, '…', size=30, bold=True)
            numbers[key].pack(anchor='w', padx=14, pady=(0, 4))
            self.button(card, 'Consulter', lambda key=key: self.navigate(key), secondary=True,
                        width=95).pack(anchor='w', padx=14, pady=(0, 14))
        events_panel = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=14)
        events_panel.grid(row=1, column=0, sticky='ew', pady=(0, 16))
        self.label(events_panel, 'Rendez-vous par mois', size=17, bold=True).pack(anchor='w', padx=20, pady=(16, 3))
        event_note = self.label(events_panel, 'Les six derniers mois, selon la date prévue.', size=12, muted=True,
                                wraplength=620, anchor='w')
        event_note.pack(fill='x', padx=20, pady=(0, 8))
        expenses_panel = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=14)
        expenses_panel.grid(row=2, column=0, sticky='ew', pady=(0, 16))
        self.label(expenses_panel, 'Décaissements payés par motif', size=17, bold=True).pack(
            anchor='w', padx=20, pady=(16, 3))
        expense_note = self.label(expenses_panel, 'Toutes les dates · Factures payées uniquement.', size=12,
                                  muted=True, wraplength=620, anchor='w')
        expense_note.pack(fill='x', padx=20, pady=(0, 8))
        if not allowed(self.user['role'], 'finances'):
            expenses_panel.grid_remove()
        alert_note = self.label(body, 'Vérification des alertes…', size=13, wraplength=650, anchor='w')
        alert_note.grid(row=3, column=0, sticky='ew', pady=8)
        self.alert_label = alert_note
        status = self.label(body, 'Chargement des indicateurs…', muted=True, wraplength=650, anchor='w')
        status.grid(row=4, column=0, sticky='ew', pady=8)

        def loaded(data):
            for key, value in data['counts'].items():
                numbers[key].configure(text=str(value))
            dark = ctk.get_appearance_mode() == 'Dark'
            self.mount_chart(events_panel, event_figure(data['months'], dark))
            if 'finances' in data['counts']:
                self.mount_chart(expenses_panel, spending_figure(data['spending'], dark))
            months = data['months']
            note = f"Période {months[0][0]} à {months[-1][0]} · Selon la date prévue."
            if data['invalid_dates']:
                note += f" {data['invalid_dates']} date(s) ancienne(s) ou invalide(s) exclue(s)."
            event_note.configure(text=note)
            if data['invalid_amounts']:
                expense_note.configure(text='Toutes les dates · Factures payées uniquement. '+
                                       f"{data['invalid_amounts']} montant(s) invalide(s) exclu(s).")
            status.configure(text='Indicateurs calculés à partir de vos enregistrements.')
            alerts = data['alerts']
            text = f"Aujourd’hui : {alerts['today_events']} rendez-vous."
            if alerts['has_finances']:
                text += f" Factures en retard : {alerts['overdue_invoices']}."
                if alerts['unknown_due_dates']:
                    text += f" {alerts['unknown_due_dates']} facture(s) non payée(s) sans échéance."
                if alerts['invalid_due_dates']:
                    text += f" {alerts['invalid_due_dates']} échéance(s) invalide(s)."
            if alerts['invalid_event_dates']:
                text += f" {alerts['invalid_event_dates']} date(s) de rendez-vous non interprétable(s)."
            alert_note.configure(text=text, text_color=('#B42318', '#FF9D97') if alerts['overdue_invoices'] else TEXT)
        actor_id = self.user['id']
        def load_home():
            data = statistics_snapshot(actor_id=actor_id)
            data['alerts'] = alerts_snapshot(actor_id)
            return data
        self.run_task(load_home, loaded, error_label=status)

    def records(self, key, page, notice=''):
        module = MODULES[key]
        current_page = [page]
        loading = [True]
        serial = [0]
        actor_id = self.user['id']
        can_write = allowed(self.user['role'], key, 'write')
        self.heading(module.title, notice or ('Recherchez, puis sélectionnez une ligne.' if can_write else
                     'Consultation et export · Recherchez dans les enregistrements.'),
                     lambda: self.navigate(key, current_page[0]))
        self.content.grid_rowconfigure(1, weight=1)
        panel = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=12)
        panel.grid(row=1, column=0, sticky='nsew')
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)
        toolbar = ctk.CTkFrame(panel, fg_color='transparent')
        toolbar.grid(row=0, column=0, columnspan=2, sticky='ew', padx=12, pady=(12, 0))
        add = self.button(toolbar, 'Ajouter', lambda: self.show_form(key), width=110)
        add.pack(side='left', padx=(0, 10))
        add.configure(state='normal' if can_write else 'disabled')
        self.record_add_button = add
        filter_bar = ctk.CTkFrame(panel, fg_color='transparent')
        filter_bar.grid(row=1, column=0, columnspan=2, sticky='ew', padx=12, pady=(12, 0))
        filter_bar.grid_columnconfigure(0, weight=1)
        saved_search, saved_status = self.list_filters.get(key, ('', 'Tous'))
        search_text = StringVar(master=self, value=saved_search)
        self.search_variable = search_text
        search = ctk.CTkEntry(filter_bar, textvariable=search_text, height=40, font=(FONT, 14))
        search.grid(row=0, column=0, sticky='ew')
        self.search_entry = search
        self.status_filter = None
        choice = None
        if key in FILTER_OPTIONS:
            choice = ctk.CTkOptionMenu(filter_bar, values=list(FILTER_OPTIONS[key]), height=40,
                                       width=155, font=(FONT, 13), fg_color=ACCENT, button_color=HOVER)
            choice.grid(row=0, column=1, padx=(10, 0))
            choice.set(saved_status)
            self.status_filter = choice
        tree = ttk.Treeview(panel, columns=module.columns+('alert',), show='headings', style='PM.Treeview')
        tree.grid(row=2, column=0, sticky='nsew', padx=(12, 0), pady=(12, 0))
        for column, title in zip(module.columns, module.headings):
            tree.heading(column, text=title)
            tree.column(column, width=65 if column == 'id' else 150, minwidth=60, stretch=False)
        tree.heading('alert', text='Alerte')
        tree.column('alert', width=120, stretch=False)
        self.apply_alert_theme(tree)
        vertical = ctk.CTkScrollbar(panel, command=tree.yview)
        vertical.grid(row=2, column=1, sticky='ns', pady=12)
        horizontal = ctk.CTkScrollbar(panel, command=tree.xview, orientation='horizontal')
        horizontal.grid(row=3, column=0, sticky='ew', padx=12, pady=6)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.record_tree = tree

        def selected_id():
            selected = tree.selection()
            return int(selected[0]) if selected and not loading[0] else None

        def edit_selected():
            identifier = selected_id()
            if identifier is not None and can_write:
                self.show_form(key, identifier, current_page[0])

        def remove_selected():
            identifier = selected_id()
            if identifier is None or not can_write:
                return
            values = tree.item(str(identifier), 'values')
            name = values[1] if len(values) > 1 else str(identifier)
            if not messagebox.askyesno('Supprimer', f'Supprimer « {name} » (ID {identifier}) ?', parent=self):
                return
            self.run_task(lambda: delete_record(key, identifier, actor_id=actor_id),
                          lambda _: self.navigate(key, current_page[0], notice='Enregistrement supprimé.'),
                          button=remove, error_label=status)

        edit = self.button(toolbar, 'Modifier', edit_selected, secondary=True, width=100)
        edit.pack(side='left', padx=(0, 10))
        remove = self.button(toolbar, 'Supprimer', remove_selected, secondary=True, width=100)
        remove.pack(side='left')
        self.record_edit_button, self.record_delete_button = edit, remove

        def selection_changed(_):
            state = 'normal' if tree.selection() and not loading[0] and can_write else 'disabled'
            edit.configure(state=state)
            remove.configure(state=state)
        tree.bind('<<TreeviewSelect>>', selection_changed)
        tree.bind('<Double-1>', lambda _: edit_selected())
        footer = ctk.CTkFrame(self.content, fg_color='transparent')
        footer.grid(row=2, column=0, sticky='ew', pady=(14, 0))
        footer.grid_columnconfigure(0, weight=1)
        status = self.label(footer, 'Chargement…', muted=True)
        status.grid(row=0, column=0, sticky='w')
        self.list_status = status
        previous = self.button(footer, 'Précédent', lambda: self.navigate(key, current_page[0]-1), secondary=True, width=100)
        previous.grid(row=0, column=1, padx=8)
        following = self.button(footer, 'Suivant', lambda: self.navigate(key, current_page[0]+1), secondary=True, width=100)
        following.grid(row=0, column=2)

        def export(suffix, button):
            term = search.get()
            selected_status = choice.get() if choice is not None else 'Tous'
            destination = filedialog.asksaveasfilename(parent=self, title='Exporter les résultats filtrés',
                initialfile=f'PersonalManager_{key}_{date.today().isoformat()}{suffix}',
                defaultextension=suffix, filetypes=[('Excel' if suffix == '.xlsx' else 'PDF', '*'+suffix)])
            if not destination:
                return
            status.configure(text='Export en cours…')
            self.run_task(lambda: export_report(key, destination, actor_id, term, selected_status),
                          lambda count: status.configure(text=f'Export terminé : {count} ligne(s).'),
                          button=button, error_label=status)
        excel = self.button(toolbar, 'Excel', lambda: export('.xlsx', excel), secondary=True, width=80)
        excel.pack(side='right', padx=(10, 0))
        pdf = self.button(toolbar, 'PDF', lambda: export('.pdf', pdf), secondary=True, width=80)
        pdf.pack(side='right', padx=(10, 0))
        self.excel_export_button, self.pdf_export_button = excel, pdf

        def refresh(target_page=0):
            self.cancel_search()
            term = search.get()
            selected_status = choice.get() if choice is not None else 'Tous'
            self.list_filters[key] = (term, selected_status)
            serial[0] += 1
            request_number = serial[0]
            loading[0] = True
            for button in (edit, remove, previous, following):
                button.configure(state='disabled')
            status.configure(text='Recherche en cours…')

            def loaded(result):
                if request_number != serial[0]:
                    return
                rows, total = result
                last_page = max(0, math.ceil(total/25)-1)
                if target_page > last_page:
                    refresh(last_page)
                    return
                current_page[0] = target_page
                loading[0] = False
                for item in tree.get_children():
                    tree.delete(item)
                for row in rows:
                    tag, label = record_alert(key, row)
                    tree.insert('', 'end', iid=str(row[0]),
                                values=[str(value) if value is not None else '—' for value in row]+[label],
                                tags=(tag,) if tag else ())
                status.configure(text='Aucun résultat.' if total == 0 else
                                 f'{total} résultats · Page {target_page+1}/{last_page+1}')
                previous.configure(state='normal' if target_page > 0 else 'disabled')
                following.configure(state='normal' if target_page < last_page else 'disabled')

            def failed(message):
                if request_number == serial[0]:
                    status.configure(text=message)
            self.run_task(lambda: list_records(key, target_page, search=term, status=selected_status, actor_id=actor_id),
                          loaded, error_callback=failed)

        def changed(*_):
            self.cancel_search()
            # Invalidate the previous query immediately, before the debounce expires.
            serial[0] += 1
            self.list_filters[key] = (search.get(), choice.get() if choice is not None else 'Tous')
            loading[0] = True
            for button in (edit, remove, previous, following):
                button.configure(state='disabled')
            self.search_timer = self.after(250, lambda: refresh(0))

        def clear_filters():
            search.delete(0, 'end')
            if choice is not None:
                choice.set('Tous')
            refresh(0)
        search_text.trace_add('write', changed)
        if choice is not None:
            choice.configure(command=lambda _: refresh(0))
        self.button(filter_bar, 'Effacer', clear_filters, secondary=True, width=90).grid(row=0, column=2, padx=(10, 0))
        self.refresh_search = refresh
        refresh(page)

    def profile(self):
        self.heading('Mon compte', 'Vos informations personnelles.', lambda: self.navigate('profile'))
        card = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=14)
        card.grid(row=1, column=0, sticky='ew')
        status = self.label(card, 'Chargement…', muted=True)
        status.pack(anchor='w', padx=25, pady=25)
        identifier = self.user['id']

        def loaded(data):
            status.destroy()
            for key, title in (('fullname', 'Nom utilisateur'), ('email', 'E-mail'),
                               ('phone', 'Téléphone'), ('gender', 'Genre')):
                self.label(card, title, muted=True, size=12).pack(anchor='w', padx=25, pady=(18, 0))
                self.label(card, data[key], size=17, wraplength=700, anchor='w').pack(
                    fill='x', padx=25, pady=(0, 12))
        self.run_task(lambda: user_profile(identifier, actor_id=identifier), loaded, error_label=status)

    def show_form(self, key, identifier=None, page=0):
        if not allowed(self.user['role'], key, 'write'):
            messagebox.showerror('Accès refusé', 'Ce module est en consultation pour votre rôle.', parent=self)
            return
        actor_id = self.user['id']
        self.current_view = 'form:'+key
        self.clear_content()
        module = MODULES[key]
        self.heading(('Modifier' if identifier is not None else 'Ajouter')+' · '+module.title,
                     'Champs obligatoires, sauf indication contraire.', lambda: self.navigate(key, page), action_label='Retour')
        self.content.grid_rowconfigure(1, weight=1)
        container = ctk.CTkFrame(self.content, fg_color='transparent')
        container.grid(row=1, column=0, sticky='nsew')
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        status = self.label(container, 'Chargement du formulaire…', muted=True)
        status.grid(row=0, column=0, sticky='nw', pady=16)

        def loaded(values):
            status.destroy()
            self.render_form(container, key, values, identifier, page)
        if identifier is None:
            loaded(initial_values(key))
        else:
            self.run_task(lambda: get_record(key, identifier, actor_id=actor_id), loaded, error_label=status)

    def render_form(self, container, key, values, identifier, page):
        scroll = ctk.CTkScrollableFrame(container, fg_color=SURFACE, corner_radius=14)
        scroll.grid(row=0, column=0, sticky='nsew')
        scroll.grid_columnconfigure((0, 1), weight=1, uniform='fields')
        widgets = {}
        self.form_fields = widgets
        for index, field in enumerate(form_fields(key)):
            cell = ctk.CTkFrame(scroll, fg_color='transparent')
            cell.grid(row=index//2, column=index%2, sticky='ew', padx=18, pady=12)
            self.label(cell, field.label, size=13).pack(anchor='w', pady=(0, 7))
            value = str(values.get(field.key) or '').strip()
            if field.choices:
                widget = ctk.CTkOptionMenu(cell, values=list(field.choices), height=42,
                                           font=(FONT, 14), fg_color=ACCENT, button_color=HOVER)
                widget.set(value)
            else:
                widget = ctk.CTkEntry(cell, height=42, font=(FONT, 14))
                widget.insert(0, value)
            widget.pack(fill='x')
            widgets[field.key] = widget
        status = self.label(container, '', size=13, wraplength=650, anchor='w')
        status.configure(text_color=('#B42318', '#FF9D97'))
        status.grid(row=1, column=0, sticky='ew', pady=(14, 6))
        self.form_status = status
        actions = ctk.CTkFrame(container, fg_color='transparent')
        actions.grid(row=2, column=0, sticky='ew', pady=8)

        def submit():
            # Capture Entry values on the Tk thread before scheduling the SQL work.
            payload = {name: widget.get() for name, widget in widgets.items()}
            actor_id = self.user['id']
            status.configure(text='Enregistrement en cours…')
            self.run_task(lambda: save_record(key, payload, identifier, actor_id=actor_id),
                          lambda _: self.navigate(key, page, notice='Modifications enregistrées.' if identifier
                                                  is not None else 'Enregistrement ajouté.'),
                          button=save, error_label=status)
        save = self.button(actions, 'Enregistrer', submit, width=160)
        save.pack(side='left', padx=(0, 12))
        self.form_save_button = save
        self.button(actions, 'Annuler', lambda: self.navigate(key, page), secondary=True, width=120).pack(side='left')

    def users(self):
        self.heading('Permissions', 'Les nouveaux comptes sont employés. Gardez au moins un administrateur.',
                     lambda: self.navigate('users'))
        self.content.grid_rowconfigure(1, weight=1)
        panel = ctk.CTkFrame(self.content, fg_color='transparent')
        panel.grid(row=1,column=0,sticky='nsew')
        panel.grid_rowconfigure(0,weight=1)
        panel.grid_columnconfigure(0,weight=1)
        tree = ttk.Treeview(panel, columns=('id', 'fullname', 'email', 'role'),
                            show='headings', style='PM.Treeview')
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar = ctk.CTkScrollbar(panel,command=tree.yview)
        scrollbar.grid(row=0,column=1,sticky='ns')
        tree.configure(yscrollcommand=scrollbar.set)
        for key, title in zip(('id', 'fullname', 'email', 'role'), ('ID', 'Compte', 'E-mail', 'Rôle')):
            tree.heading(key, text=title)
            tree.column(key, width=65 if key == 'id' else 170)
        self.user_tree = tree
        bar = ctk.CTkFrame(self.content, fg_color='transparent')
        bar.grid(row=2, column=0, sticky='ew', pady=15)
        choice = ctk.CTkOptionMenu(bar, values=list(ROLE_LABELS.values()), height=42,
                                 fg_color=ACCENT, button_color=HOVER)
        choice.pack(side='left', padx=(0, 12))
        choice.set(ROLE_LABELS['employee'])
        self.role_choice = choice
        status = self.label(bar, '', size=12, wraplength=300)
        actor_id = self.user['id']
        def apply_role():
            selection = tree.selection()
            if not selection:
                status.configure(text='Sélectionnez un compte.')
                return
            target_id = int(selection[0])
            role = next(key for key, label in ROLE_LABELS.items() if label == choice.get())
            if not messagebox.askyesno('Permissions', 'Confirmer le changement de rôle ?', parent=self):
                return
            self.run_task(lambda: set_role(actor_id, target_id, role), lambda _: self.show_shell(),
                          button=save, error_label=status)
        save = self.button(bar, 'Appliquer le rôle', apply_role, width=160)
        save.pack(side='left', padx=(0, 12))
        self.role_save_button = save
        status.pack(side='left')
        def loaded(rows):
            for identifier, name, email, role in rows:
                tree.insert('', 'end', iid=str(identifier), values=(identifier, name, email, ROLE_LABELS[role]))
        self.run_task(lambda: list_users(actor_id), loaded, error_label=status)
