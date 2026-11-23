import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from core.validation import validate_measurements
from core.classifier import FEATURES, DISPLAY_FEATURES
from core.statistics import build_summary
from core.search import search_records
from core.warnings import measurement_warnings
from storage.import_export import import_csv, export_records
from gui.styles import *

class IrisApp(tk.Tk):
    def __init__(self, model, store):
        super().__init__()
        self.model, self.store = model, store
        self.title("Iris Studio | Dataset Classifier")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg=BG)
        self._style()
        self._layout()
        self.show_page("Dashboard")

    def _style(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#EDF2FA", foreground=TEXT,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#DCE7FF")], foreground=[("selected", TEXT)])
        style.configure("TCombobox", padding=8, font=("Segoe UI", 10))

    def _layout(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="✿  IRIS STUDIO", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(28, 4))
        tk.Label(self.sidebar, text="DATA CLASSIFIER", bg=SIDEBAR, fg="#9EACC2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 35))
        self.nav_buttons = {}
        for name, symbol in [("Dashboard","⌂"),("New Prediction","+"),("Records","▤"),("Analytics","▥")]:
            b = tk.Button(self.sidebar, text=f"   {symbol}   {name}", anchor="w", relief="flat",
                          bd=0, bg=SIDEBAR, fg="#D4DDED", activebackground="#293B59",
                          activeforeground="white", font=("Segoe UI", 11), padx=14, pady=13,
                          command=lambda n=name: self.show_page(n))
            b.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[name] = b
        tk.Frame(self.sidebar, bg="#34445E", height=1).pack(fill="x", padx=20, pady=22)
        tk.Label(self.sidebar, text="MODEL STATUS", bg=SIDEBAR, fg="#9EACC2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25)
        tk.Label(self.sidebar, text="●  Random Forest ready", bg=SIDEBAR, fg="#75D5A9",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=25, pady=8)
        tk.Label(self.sidebar, text="Offline • Local storage", bg=SIDEBAR, fg="#9EACC2",
                 font=("Segoe UI", 8)).pack(side="bottom", anchor="w", padx=25, pady=22)
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.content, bg=BG)
        self.header.pack(fill="x", padx=34, pady=(26, 10))
        self.page_title = tk.Label(self.header, text="", bg=BG, fg=TEXT, font=("Segoe UI", 23, "bold"))
        self.page_title.pack(side="left")
        self.page_subtitle = tk.Label(self.header, text="", bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.page_subtitle.pack(side="left", padx=15, pady=(10,0))
        self.actions = tk.Frame(self.header, bg=BG)
        self.actions.pack(side="right")
        self.body = tk.Frame(self.content, bg=BG)
        self.body.pack(fill="both", expand=True, padx=34, pady=(10, 28))

    def clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def card(self, parent, title, value, note="", accent=PRIMARY):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        tk.Frame(box, bg=accent, height=4).pack(fill="x")
        tk.Label(box, text=title.upper(), bg=PANEL, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=17, pady=(15,4))
        tk.Label(box, text=value, bg=PANEL, fg=TEXT, font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=17)
        tk.Label(box, text=note, bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(2,15))
        return box

    def button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         bg=PRIMARY if primary else "#E9EFFB", fg="white" if primary else PRIMARY,
                         activebackground=PRIMARY_DARK if primary else "#DCE6FA",
                         activeforeground="white" if primary else PRIMARY,
                         font=("Segoe UI", 9, "bold"), padx=16, pady=10, cursor="hand2")

    def show_page(self, name):
        self.current_page = name
        for n,b in self.nav_buttons.items():
            b.configure(bg="#293B59" if n == name else SIDEBAR,
                        fg="white" if n == name else "#D4DDED")
        self.page_title.configure(text=name)
        self.page_subtitle.configure(text={
            "Dashboard":"Your Iris classification workspace",
            "New Prediction":"Enter flower measurements to classify",
            "Records":"Search and manage saved predictions",
            "Analytics":"Understand your saved prediction data"
        }[name])
        for w in self.actions.winfo_children(): w.destroy()
        self.clear_body()
        if name == "Dashboard": self.dashboard_page()
        elif name == "New Prediction": self.prediction_page()
        elif name == "Records": self.records_page()
        else: self.analytics_page()

    def dashboard_page(self):
        s = build_summary(self.store.records)
        cards = tk.Frame(self.body, bg=BG)
        cards.pack(fill="x")
        values = [
            ("Total records", str(s["total_records"]), "Saved predictions", PRIMARY),
            ("Model accuracy", f"{self.model.accuracy:.1%}", "5-fold cross-validation", SUCCESS),
            ("Average confidence", f"{s['average_confidence']:.1%}", "Across saved predictions", "#7C5CE7"),
            ("Species detected", str(len(s["species_counts"])), "Of 3 Iris species", WARNING)
        ]
        for i, item in enumerate(values):
            c = self.card(cards, *item)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 10, 0))
            cards.grid_columnconfigure(i, weight=1)
        lower = tk.Frame(self.body, bg=BG)
        lower.pack(fill="both", expand=True, pady=20)
        left = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0,10))
        tk.Label(left, text="Welcome to Iris Studio", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(22,7))
        tk.Label(left, text="Classify Iris flowers using four measurements and a locally trained Random Forest model.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 10), wraplength=500, justify="left").pack(anchor="w", padx=22)
        self.button(left, "＋  Create prediction", lambda:self.show_page("New Prediction"), True).pack(anchor="w", padx=22, pady=20)
        tk.Label(left, text="RECENT PREDICTIONS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(5,8))
        for r in self.store.records[-5:][::-1]:
            tk.Label(left, text=f"•  {r.get('species','Unknown')}     {r.get('confidence',0):.1%} confidence",
                     bg=PANEL, fg=TEXT, font=("Segoe UI", 10)).pack(anchor="w", padx=25, pady=4)
        if not self.store.records:
            tk.Label(left, text="No predictions yet. Your saved results will appear here.",
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=8)
        right = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, width=270)
        right.pack(side="right", fill="y")
        tk.Label(right, text="QUICK ACTIONS", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=(20,10))
        self.button(right, "New prediction", lambda:self.show_page("New Prediction"), True).pack(fill="x", padx=16, pady=5)
        self.button(right, "Import CSV dataset", self.import_file).pack(fill="x", padx=16, pady=5)
        self.button(right, "Export reports", self.export_files).pack(fill="x", padx=16, pady=5)
        self.button(right, "View analytics", lambda:self.show_page("Analytics")).pack(fill="x", padx=16, pady=5)

    def prediction_page(self):
        outer = tk.Frame(self.body, bg=BG)
        outer.pack(fill="both", expand=True)
        form = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        form.pack(side="left", fill="y", padx=(0,14))
        tk.Label(form, text="Flower measurements", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=24, pady=(23,4))
        tk.Label(form, text="All values are in centimeters (cm).", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(0,16))
        self.measure_entries = {}
        defaults = ["5.1","3.5","1.4","0.2"]
        for label, key, default in zip(DISPLAY_FEATURES, FEATURES, defaults):
            tk.Label(form, text=label, bg=PANEL, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=24, pady=(8,4))
            e = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1, highlightthickness=0, width=28)
            e.insert(0, default)
            e.pack(anchor="w", padx=24, ipady=8)
            self.measure_entries[key] = e
        self.button(form, "Run prediction  →", self.make_prediction, True).pack(fill="x", padx=24, pady=22)
        result = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        result.pack(side="left", fill="both", expand=True)
        tk.Label(result, text="Prediction result", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=24, pady=(23,5))
        self.result_species = tk.Label(result, text="Awaiting measurements", bg=PANEL, fg=MUTED,
                                       font=("Segoe UI", 22, "bold"))
        self.result_species.pack(anchor="w", padx=24, pady=(28,4))
        self.result_conf = tk.Label(result, text="Enter values and run the classifier.", bg=PANEL, fg=MUTED,
                                    font=("Segoe UI", 10))
        self.result_conf.pack(anchor="w", padx=24)
        self.result_warnings = tk.Label(result, text="", bg=PANEL, fg=WARNING,
                                        font=("Segoe UI", 9), justify="left", wraplength=480)
        self.result_warnings.pack(anchor="w", padx=24, pady=18)
        self.prob_labels = {}
        tk.Label(result, text="CLASS PROBABILITIES", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(15,8))
        for species in self.model.species:
            row = tk.Frame(result, bg=PANEL)
            row.pack(fill="x", padx=24, pady=7)
            tk.Label(row, text=species, bg=PANEL, fg=TEXT, width=13, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="—", bg=PANEL, fg=PRIMARY, font=("Segoe UI", 10, "bold"))
            lbl.pack(side="right")
            self.prob_labels[species] = lbl

    def make_prediction(self):
        try:
            values = validate_measurements([self.measure_entries[k].get().strip() for k in FEATURES])
            result = self.model.predict(values)
            warnings = measurement_warnings(values, self.model.ranges)
            record = dict(zip(FEATURES, values))
            record.update(result)
            record["source"] = "Desktop GUI"
            self.store.add(record)
            self.result_species.configure(text=result["species"], fg=SUCCESS)
            self.result_conf.configure(text=f"Confidence: {result['confidence']:.1%}  •  Saved successfully")
            self.result_warnings.configure(text="\n".join("• " + w for w in warnings))
            for species, probability in result["probabilities"].items():
                self.prob_labels[species].configure(text=f"{probability:.1%}")
            messagebox.showinfo("Prediction complete", f"Predicted species: {result['species']}\nThe record has been saved.")
        except ValueError as exc:
            messagebox.showerror("Check your measurements", str(exc))

    def records_page(self):
        bar = tk.Frame(self.body, bg=BG)
        bar.pack(fill="x", pady=(0,12))
        self.search_var = tk.StringVar()
        search = tk.Entry(bar, textvariable=self.search_var, font=("Segoe UI", 10), relief="solid", bd=1)
        search.pack(side="left", fill="x", expand=True, ipady=9, padx=(0,10))
        search.insert(0, "")
        self.species_var = tk.StringVar(value="All")
        combo = ttk.Combobox(bar, textvariable=self.species_var, values=["All"]+self.model.species, state="readonly", width=16)
        combo.pack(side="left", padx=(0,10), ipady=4)
        self.button(bar, "Search", self.refresh_records, True).pack(side="left")
        self.button(bar, "Import CSV", self.import_file).pack(side="left", padx=8)
        self.button(bar, "Export", self.export_files).pack(side="left")
        tablebox = tk.Frame(self.body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        tablebox.pack(fill="both", expand=True)
        cols = ("id","species","confidence","sepal_length","sepal_width","petal_length","petal_width","created_at")
        self.tree = ttk.Treeview(tablebox, columns=cols, show="headings")
        headings = ["Record ID","Species","Confidence","Sepal L","Sepal W","Petal L","Petal W","Created"]
        widths = [190,110,100,80,80,80,80,160]
        for col, title, width in zip(cols, headings, widths):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="center")
        yscroll = ttk.Scrollbar(tablebox, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        yscroll.pack(side="right", fill="y", pady=8)
        self.refresh_records()

    def refresh_records(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = search_records(self.store.records, self.search_var.get(), self.species_var.get())
        for r in rows:
            self.tree.insert("", "end", values=(r.get("id",""),r.get("species",""),f"{r.get('confidence',0):.1%}",
                r.get("sepal_length",""),r.get("sepal_width",""),r.get("petal_length",""),r.get("petal_width",""),
                r.get("created_at","")))

    def analytics_page(self):
        s = build_summary(self.store.records)
        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x")
        for i, (title, val, note, color) in enumerate([
            ("Predictions",str(s["total_records"]),"Total saved records",PRIMARY),
            ("Avg. confidence",f"{s['average_confidence']:.1%}","Mean model confidence",SUCCESS),
            ("Species classes",str(len(s["species_counts"])),"Classes represented", "#7C5CE7")]):
            self.card(top,title,val,note,color).grid(row=0,column=i,sticky="nsew",padx=(0,10))
            top.grid_columnconfigure(i,weight=1)
        chartbox = tk.Frame(self.body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        chartbox.pack(fill="both", expand=True, pady=18)
        tk.Label(chartbox, text="Species distribution", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=16)
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            fig = Figure(figsize=(7,3.4), dpi=100)
            ax = fig.add_subplot(111)
            counts = s["species_counts"]
            labels = list(counts) if counts else ["No records"]
            vals = list(counts.values()) if counts else [0]
            bars = ax.bar(labels, vals, color=["#3867E8","#25A67A","#9B7BE8"][:len(labels)])
            ax.set_ylabel("Number of predictions")
            ax.set_facecolor("#FFFFFF")
            fig.patch.set_facecolor("#FFFFFF")
            ax.spines[["top","right"]].set_visible(False)
            ax.grid(axis="y", alpha=.18)
            ax.set_axisbelow(True)
            canvas = FigureCanvasTkAgg(fig, master=chartbox)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0,15))
        except Exception as exc:
            tk.Label(chartbox, text=f"Chart unavailable: {exc}", bg=PANEL, fg=MUTED).pack(pady=30)
        averages = tk.Frame(self.body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        averages.pack(fill="x")
        tk.Label(averages, text="Average measurements (cm)", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=12)
        vals = [s[k+"_average"] for k in FEATURES]
        tk.Label(averages, text="     ".join(f"{k.replace('_',' ').title()}: {v:.2f}" if v is not None else f"{k}: —"
                 for k,v in zip(FEATURES,vals)), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(0,14))

    def import_file(self):
        path = filedialog.askopenfilename(title="Select Iris CSV", filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path: return
        try:
            count, errors = import_csv(path, self.model, self.store)
            message = f"Successfully imported {count} row(s)."
            if errors: message += "\n\nSome rows were skipped:\n" + "\n".join(errors[:12])
            messagebox.showinfo("Import result", message)
            self.show_page("Records")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Import failed", str(exc))

    def export_files(self):
        folder = filedialog.askdirectory(title="Choose report folder")
        if not folder: return
        try:
            paths = export_records(self.store.records, folder)
            messagebox.showinfo("Export complete", "Created report files:\n" + "\n".join(str(p) for p in paths))
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))
