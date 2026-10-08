"""Single-window CustomTkinter preview, with background database operations."""
import math
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from tkinter import messagebox, ttk

import customtkinter as ctk

from backend.auth import AuthenticationError, authenticate_user, register_user
from backend.dashboard import MODULES, dashboard_counts, list_records, user_profile
from backend.migrations import MigrationError, migrate_passwords
from backend.management import delete_record, form_fields, get_record, initial_values, save_record

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
        self.title('PersonalManager — Aperçu de la nouvelle interface')
        self.geometry('1180x760')
        self.minsize(1000, 680)
        self.configure(fg_color=BACKGROUND)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.generation = 0
        self.polls = set()
        self.user = None
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
        self.run_task(migrate_passwords, lambda _: self.show_login(), fatal=True)

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
        self.generation += 1
        for widget in self.winfo_children():
            widget.destroy()
        self.screen = ctk.CTkFrame(self, fg_color=BACKGROUND, corner_radius=0)
        self.screen.grid(row=0, column=0, sticky='nsew')

    def clear_content(self):
        self.generation += 1
        for widget in self.content.winfo_children():
            widget.destroy()
        self.content.grid_rowconfigure(1, weight=0)

    def run_task(self, action, success, button=None, error_label=None, fatal=False):
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
            if error_label is not None:
                error_label.configure(text=text)
            else:
                messagebox.showerror('PersonalManager', text, parent=self)
            if fatal:
                self.close()

        poll_id = [self.after(50, poll)]
        self.polls.add(poll_id[0])

    def close(self):
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
        self.replace_root()
        self.screen.grid_rowconfigure(0, weight=1)
        self.screen.grid_columnconfigure(1, weight=1)
        sidebar = ctk.CTkFrame(self.screen, width=220, fg_color='#102239', corner_radius=0)
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(8, weight=1)
        ctk.CTkLabel(sidebar, text='PM / PersonalManager', text_color='#67D4DE',
                     font=(FONT, 16, 'bold')).grid(row=0, column=0, padx=20, pady=(30, 8), sticky='w')
        ctk.CTkLabel(sidebar, text=self.user['fullname'], text_color='#AABBD0',
                     font=(FONT, 13), wraplength=175).grid(row=1, column=0, padx=20, pady=(0, 28), sticky='w')
        self.navigation = {}
        for row, (key, title) in enumerate([('home', 'Vue d’ensemble')]+
                                           [(key, module.title) for key, module in MODULES.items()]+
                                           [('profile', 'Mon compte')], 2):
            button = ctk.CTkButton(sidebar, text=title, anchor='w', height=44,
                                   font=(FONT, 14), corner_radius=8, fg_color='transparent',
                                   hover_color='#203B55', command=lambda key=key: self.navigate(key))
            button.grid(row=row, column=0, sticky='ew', padx=14, pady=4)
            self.navigation[key] = button
        theme_menu = ctk.CTkOptionMenu(sidebar, values=['Sombre', 'Clair'], command=self.change_theme,
                          fg_color='#203B55', button_color='#2B4C67', font=(FONT, 13))
        theme_menu.set('Clair' if ctk.get_appearance_mode() == 'Light' else 'Sombre')
        theme_menu.grid(row=9, column=0, padx=18, pady=10, sticky='ew')
        self.button(sidebar, 'Se déconnecter', self.show_login).grid(row=10, column=0,
                                                                  padx=18, pady=(5, 25), sticky='ew')
        self.content = ctk.CTkFrame(self.screen, fg_color='transparent')
        self.content.grid(row=0, column=1, sticky='nsew', padx=30, pady=28)
        self.content.grid_columnconfigure(0, weight=1)
        self.navigate('home')

    def change_theme(self, selection):
        ctk.set_appearance_mode('Light' if selection == 'Clair' else 'Dark')
        self.apply_table_theme()

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

    def navigate(self, key, page=0, notice=''):
        self.clear_content()
        for name, button in self.navigation.items():
            button.configure(fg_color=ACCENT if name == key else 'transparent')
        if key == 'home':
            self.home()
        elif key == 'profile':
            self.profile()
        else:
            self.records(key, page, notice)

    def heading(self, title, subtitle, refresh, action_label='Actualiser'):
        bar = ctk.CTkFrame(self.content, fg_color='transparent')
        bar.grid(row=0, column=0, sticky='ew', pady=(0, 24))
        bar.grid_columnconfigure(0, weight=1)
        self.label(bar, title, size=28, bold=True).grid(row=0, column=0, sticky='w')
        self.label(bar, subtitle, muted=True).grid(row=1, column=0, sticky='w', pady=5)
        self.button(bar, action_label, refresh, secondary=True, width=110).grid(row=0, column=1, rowspan=2, padx=(10, 0))

    def home(self):
        self.heading('Vue d’ensemble', date.today().strftime('%d/%m/%Y')+' · Votre activité en un coup d’œil',
                     lambda: self.navigate('home'))
        cards = ctk.CTkFrame(self.content, fg_color='transparent')
        cards.grid(row=1, column=0, sticky='ew')
        cards.grid_columnconfigure((0, 1), weight=1, uniform='cards')
        numbers = {}
        for index, (key, module) in enumerate(MODULES.items()):
            card = ctk.CTkFrame(cards, fg_color=SURFACE, corner_radius=14)
            card.grid(row=index//2, column=index%2, sticky='ew', padx=(0, 12), pady=(0, 14))
            self.label(card, module.title, muted=True).pack(anchor='w', padx=22, pady=(18, 0))
            numbers[key] = self.label(card, '…', size=38, bold=True)
            numbers[key].pack(anchor='w', padx=22, pady=(0, 10))
            self.button(card, 'Consulter', lambda key=key: self.navigate(key), secondary=True).pack(
                anchor='w', padx=22, pady=(0, 18))
        status = self.label(self.content, 'Chargement des indicateurs…', muted=True)
        status.grid(row=2, column=0, sticky='w', pady=12)

        def loaded(counts):
            for key, value in counts.items():
                numbers[key].configure(text=str(value))
            status.configure(text='Indicateurs calculés à partir de vos données locales.')
        self.run_task(dashboard_counts, loaded, error_label=status)

    def records(self, key, page, notice=''):
        module = MODULES[key]
        self.heading(module.title, notice or 'Sélectionnez une ligne pour la modifier ou la supprimer.',
                     lambda: self.navigate(key, page))
        self.content.grid_rowconfigure(1, weight=1)
        panel = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=12)
        panel.grid(row=1, column=0, sticky='nsew')
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(panel, fg_color='transparent')
        toolbar.grid(row=0, column=0, columnspan=2, sticky='ew', padx=12, pady=(12, 0))
        self.button(toolbar, 'Ajouter', lambda: self.show_form(key), width=120).pack(side='left', padx=(0, 10))
        tree = ttk.Treeview(panel, columns=module.columns, show='headings', style='PM.Treeview')
        tree.grid(row=1, column=0, sticky='nsew', padx=(12, 0), pady=(12, 0))
        for column, title in zip(module.columns, module.headings):
            tree.heading(column, text=title)
            tree.column(column, width=65 if column == 'id' else 150, minwidth=60, stretch=False)
        vertical = ctk.CTkScrollbar(panel, command=tree.yview)
        vertical.grid(row=1, column=1, sticky='ns', pady=12)
        horizontal = ctk.CTkScrollbar(panel, command=tree.xview, orientation='horizontal')
        horizontal.grid(row=2, column=0, sticky='ew', padx=12, pady=6)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.record_tree = tree

        def selected_id():
            selected = tree.selection()
            return int(selected[0]) if selected else None

        def edit_selected():
            identifier = selected_id()
            if identifier is not None:
                self.show_form(key, identifier, page)

        def remove_selected():
            identifier = selected_id()
            if identifier is None:
                return
            values = tree.item(str(identifier), 'values')
            name = values[1] if len(values) > 1 else str(identifier)
            if not messagebox.askyesno('Supprimer', f'Supprimer « {name} » (ID {identifier}) ?', parent=self):
                return
            self.run_task(lambda: delete_record(key, identifier),
                          lambda _: self.navigate(key, page, notice='Enregistrement supprimé.'),
                          button=remove, error_label=status)

        edit = self.button(toolbar, 'Modifier', edit_selected, secondary=True, width=120)
        edit.pack(side='left', padx=(0, 10))
        remove = self.button(toolbar, 'Supprimer', remove_selected, secondary=True, width=120)
        remove.pack(side='left')
        edit.configure(state='disabled')
        remove.configure(state='disabled')

        def selection_changed(_):
            state = 'normal' if tree.selection() else 'disabled'
            edit.configure(state=state)
            remove.configure(state=state)
        tree.bind('<<TreeviewSelect>>', selection_changed)
        tree.bind('<Double-1>', lambda _: edit_selected())
        footer = ctk.CTkFrame(self.content, fg_color='transparent')
        footer.grid(row=2, column=0, sticky='ew', pady=(14, 0))
        footer.grid_columnconfigure(0, weight=1)
        status = self.label(footer, 'Chargement…', muted=True)
        status.grid(row=0, column=0, sticky='w')
        previous = self.button(footer, 'Précédent', lambda: self.navigate(key, page-1), secondary=True, width=100)
        previous.grid(row=0, column=1, padx=8)
        following = self.button(footer, 'Suivant', lambda: self.navigate(key, page+1), secondary=True, width=100)
        following.grid(row=0, column=2)
        previous.configure(state='disabled')
        following.configure(state='disabled')

        def loaded(result):
            rows, total = result
            last_page = max(0, math.ceil(total/25)-1)
            if page > last_page:
                self.navigate(key, last_page)
                return
            for row in rows:
                tree.insert('', 'end', iid=str(row[0]), values=[str(value) if value is not None else '—' for value in row])
            status.configure(text='Aucun enregistrement.' if total == 0 else
                             f'{total} enregistrements · Page {page+1}/{last_page+1}')
            previous.configure(state='normal' if page > 0 else 'disabled')
            following.configure(state='normal' if page < last_page else 'disabled')
        self.run_task(lambda: list_records(key, page), loaded, error_label=status)

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
        self.run_task(lambda: user_profile(identifier), loaded, error_label=status)

    def show_form(self, key, identifier=None, page=0):
        self.clear_content()
        module = MODULES[key]
        self.heading(('Modifier' if identifier is not None else 'Ajouter')+' · '+module.title,
                     'Tous les champs sont obligatoires.', lambda: self.navigate(key, page), action_label='Retour')
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
            self.run_task(lambda: get_record(key, identifier), loaded, error_label=status)

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
            value = str(values.get(field.key, '')).strip()
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
            status.configure(text='Enregistrement en cours…')
            self.run_task(lambda: save_record(key, payload, identifier),
                          lambda _: self.navigate(key, page, notice='Modifications enregistrées.' if identifier
                                                  is not None else 'Enregistrement ajouté.'),
                          button=save, error_label=status)
        save = self.button(actions, 'Enregistrer', submit, width=160)
        save.pack(side='left', padx=(0, 12))
        self.form_save_button = save
        self.button(actions, 'Annuler', lambda: self.navigate(key, page), secondary=True, width=120).pack(side='left')
