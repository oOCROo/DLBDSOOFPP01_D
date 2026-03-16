from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os

# 1. DOMAIN (Fachklassen mit @dataclass)

@dataclass
class Pruefungsleistung(ABC):
    note: float
    datum: date | None

    def ist_bestanden(self) -> bool:
        return 0.0 < self.note <= 4.0

@dataclass
class Klausur(Pruefungsleistung):
    dauer: int

@dataclass
class Hausarbeit(Pruefungsleistung):
    seitenzahl: int

@dataclass
class Portfolio(Pruefungsleistung):
    anzahl_phasen: int

@dataclass
class Modul:
    bezeichnung: str
    ects: int
    pruefungsleistung: Pruefungsleistung

    def ist_abgeschlossen(self) -> bool:
        return self.pruefungsleistung.ist_bestanden()

@dataclass
class Semester:
    nummer: int
    # Vermeidung von geteilten Listen durch default_factory
    module: list[Modul] = field(default_factory=list)

    def modul_hinzufuegen(self, modul: Modul) -> None:
        self.module.append(modul)

@dataclass
class Studiengang:
    bezeichnung: str
    regelstudienzeit: int
    semester: list[Semester] = field(default_factory=list)

    def semester_hinzufuegen(self, semester: Semester) -> None:
        self.semester.append(semester)


# 2. SERVICE (Fachliche Berechnungslogik)

class NotenService:
    """Service-Klasse: enthält fachliche Logik, die mehrere Objekte betrifft."""
    def berechne_gesamt_ects(self, studiengang: Studiengang) -> int:
        return sum(m.ects for s in studiengang.semester for m in s.module if m.ist_abgeschlossen())

    def berechne_notendurchschnitt(self, studiengang: Studiengang) -> float:
        noten = [m.pruefungsleistung.note for s in studiengang.semester for m in s.module 
                 if m.ist_abgeschlossen() and m.pruefungsleistung.note > 0.0]
        return round(sum(noten) / len(noten), 2) if noten else 0.0


# 3. REPOSITORY (Datenzugriff/Persistenz)

class StudiengangRepository:
    """Repository: kapselt den Zugriff auf persistente Daten (JSON)."""
    def __init__(self, dateipfad: str = "studien_daten.json"):
        self.dateipfad = dateipfad

    def speichern(self, studiengang: Studiengang) -> None:
        daten = {
            "bezeichnung": studiengang.bezeichnung,
            "regelstudienzeit": studiengang.regelstudienzeit,
            "semester": []
        }
        for sem in studiengang.semester:
            sem_dict = {"nummer": sem.nummer, "module": []}
            for mod in sem.module:
                pl = mod.pruefungsleistung
                pl_dict = {
                    "art": pl.__class__.__name__,
                    "note": pl.note,
                    "datum": pl.datum.isoformat() if pl.datum else None
                }
                if isinstance(pl, Klausur): pl_dict["dauer"] = pl.dauer
                elif isinstance(pl, Hausarbeit): pl_dict["seitenzahl"] = pl.seitenzahl
                elif isinstance(pl, Portfolio): pl_dict["anzahl_phasen"] = pl.anzahl_phasen

                sem_dict["module"].append({
                    "bezeichnung": mod.bezeichnung,
                    "ects": mod.ects,
                    "pruefungsleistung": pl_dict
                })
            daten["semester"].append(sem_dict)

        with open(self.dateipfad, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4)

    def laden(self) -> Studiengang:
        if not os.path.exists(self.dateipfad):
            return self._erstelle_dummy_daten()

        with open(self.dateipfad, "r", encoding="utf-8") as f:
            daten = json.load(f)

        studiengang = Studiengang(daten["bezeichnung"], daten["regelstudienzeit"])
        for sem_data in daten["semester"]:
            semester = Semester(sem_data["nummer"])
            for mod_data in sem_data["module"]:
                pl_data = mod_data["pruefungsleistung"]
                d = date.fromisoformat(pl_data["datum"]) if pl_data["datum"] else None
                
                if pl_data["art"] == "Klausur":
                    pl = Klausur(pl_data["note"], d, pl_data.get("dauer", 90))
                elif pl_data["art"] == "Hausarbeit":
                    pl = Hausarbeit(pl_data["note"], d, pl_data.get("seitenzahl", 15))
                else:
                    pl = Portfolio(pl_data["note"], d, pl_data.get("anzahl_phasen", 3))

                modul = Modul(mod_data["bezeichnung"], mod_data["ects"], pl)
                semester.modul_hinzufuegen(modul)
            studiengang.semester_hinzufuegen(semester)
            
        return studiengang

    def _erstelle_dummy_daten(self) -> Studiengang:
        sg = Studiengang("B.Sc. Softwareentwicklung", 6)
        sem1 = Semester(1)
        sem1.modul_hinzufuegen(Modul("Mathematik I", 5, Klausur(1.3, date(2023, 2, 1), 90)))
        sem1.modul_hinzufuegen(Modul("OOP mit Python", 5, Portfolio(0.0, None, 3)))
        sg.semester_hinzufuegen(sem1)
        return sg


# 4. VIEW (GUI - nur Darstellung)

class DashboardView:
    """View: zuständig für die Darstellung, keine Berechnungslogik."""
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Studien-Dashboard (Prototyp)")
        self.root.geometry("850x500")
        self._baue_gui()

    def _baue_gui(self):
        kpi_frame = tk.Frame(self.root, pady=10)
        kpi_frame.pack(fill=tk.X)

        self.lbl_note = tk.Label(kpi_frame, text="Schnitt: -", font=("Arial", 16, "bold"))
        self.lbl_note.pack(side=tk.LEFT, padx=20)

        self.lbl_ects = tk.Label(kpi_frame, text="ECTS: 0/180", font=("Arial", 16, "bold"))
        self.lbl_ects.pack(side=tk.LEFT, padx=20)

        columns = ("semester", "modul", "art", "ects", "note", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("semester", text="Sem.")
        self.tree.heading("modul", text="Modul")
        self.tree.heading("art", text="Prüfungsart")
        self.tree.heading("ects", text="ECTS")
        self.tree.heading("note", text="Note")
        self.tree.heading("status", text="Status")
        
        self.tree.column("semester", width=50, anchor=tk.CENTER)
        self.tree.column("ects", width=50, anchor=tk.CENTER)
        self.tree.column("note", width=50, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        btn_hinzufuegen = tk.Button(btn_frame, text="Modul hinzufügen", command=self.controller.modul_hinzufuegen_dialog)
        btn_hinzufuegen.pack(side=tk.LEFT, padx=5)

        btn_note = tk.Button(btn_frame, text="Note eintragen", command=self.controller.note_eintragen_dialog)
        btn_note.pack(side=tk.LEFT, padx=5)

        btn_speichern = tk.Button(btn_frame, text="Daten speichern (Export)", command=self.controller.daten_speichern_geklickt)
        btn_speichern.pack(side=tk.LEFT, padx=5)

    def aktualisiere_anzeige(self, studiengang: Studiengang, schnitt: float, ects: int):
        self.lbl_note.config(text=f"Schnitt: {schnitt}")
        self.lbl_ects.config(text=f"ECTS: {ects} / {studiengang.regelstudienzeit * 30}")

        for item in self.tree.get_children():
            self.tree.delete(item)

        for sem in studiengang.semester:
            for mod in sem.module:
                pl = mod.pruefungsleistung
                note_str = str(pl.note) if pl.note > 0.0 else "-"
                status = "bestanden" if pl.ist_bestanden() else "offen"
                
                self.tree.insert("", tk.END, values=(
                    sem.nummer, mod.bezeichnung, pl.__class__.__name__, mod.ects, note_str, status
                ), tags=(id(mod),))


# 5. CONTROLLER (Ablaufkoordination)

class DashboardController:
    """Controller: vermittelt zwischen UI (View), Service und Repository."""
    def __init__(self, service: NotenService, repo: StudiengangRepository, root: tk.Tk):
        self.service = service
        self.repo = repo
        self.root = root
        
        self.studiengang = self.repo.laden()
        self.view = DashboardView(root, self)
        self.aktualisiere_view()

    def aktualisiere_view(self):
        schnitt = self.service.berechne_notendurchschnitt(self.studiengang)
        ects = self.service.berechne_gesamt_ects(self.studiengang)
        self.view.aktualisiere_anzeige(self.studiengang, schnitt, ects)

    def daten_speichern_geklickt(self):
        dateipfad = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")],
            title="Daten speichern unter..."
        )
        if dateipfad:
            try:
                self.repo.dateipfad = dateipfad
                self.repo.speichern(self.studiengang)
                messagebox.showinfo("Erfolg", f"Daten wurden erfolgreich gespeichert unter:\n{dateipfad}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{str(e)}")

    def modul_hinzufuegen_dialog(self):
        eingabe = simpledialog.askstring("Neues Modul", "Bitte im Format eingeben:\nSemester, Modulname, ECTS, Prüfungsart\n(z.B.: 2, Datenbanken, 5, Hausarbeit)")
        if eingabe:
            try:
                teile = [t.strip() for t in eingabe.split(",")]
                sem_nummer = int(teile[0])
                name = teile[1]
                ects = int(teile[2])
                art_eingabe = teile[3].lower() if len(teile) > 3 else "klausur"

                if art_eingabe == "hausarbeit": pl = Hausarbeit(0.0, None, 15)
                elif art_eingabe == "portfolio": pl = Portfolio(0.0, None, 3)
                else: pl = Klausur(0.0, None, 90)

                neues_modul = Modul(name, ects, pl)

                ziel_sem = next((s for s in self.studiengang.semester if s.nummer == sem_nummer), None)
                if not ziel_sem:
                    ziel_sem = Semester(sem_nummer)
                    self.studiengang.semester_hinzufuegen(ziel_sem)
                
                ziel_sem.modul_hinzufuegen(neues_modul)
                self.aktualisiere_view()
            except Exception:
                messagebox.showerror("Fehler", "Ungültige Eingabe! Bitte Format beachten.")

    def note_eintragen_dialog(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            messagebox.showwarning("Achtung", "Bitte wähle zuerst ein Modul aus!")
            return

        item_values = self.view.tree.item(selected_item[0], "values")
        modul_name = item_values[1]

        neue_note_str = simpledialog.askstring("Note eintragen", f"Bitte neue Note für '{modul_name}' eingeben:")
        if neue_note_str:
            try:
                neue_note = float(neue_note_str)
                for sem in self.studiengang.semester:
                    for mod in sem.module:
                        if mod.bezeichnung == modul_name:
                            mod.pruefungsleistung.note = neue_note
                            mod.pruefungsleistung.datum = date.today()
                self.aktualisiere_view()
            except ValueError:
                messagebox.showerror("Fehler", "Bitte eine gültige Kommazahl (mit Punkt!) eingeben.")


# 6. APPLICATION (Composition Root)

class DashboardApp:
    """Application: Startpunkt und Verdrahtung der Schichten."""
    def start(self) -> None:
        root = tk.Tk()
        # Erzeugt alle benötigten Objekte
        repo = StudiengangRepository()
        service = NotenService()
        
        # Verbindet die Schichten miteinander
        controller = DashboardController(service, repo, root)
        
        # Startet die GUI
        root.mainloop()

if __name__ == "__main__":
    DashboardApp().start()