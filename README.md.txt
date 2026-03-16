# Studien-Dashboard (Prototyp)

Dieses Repository enthält den prototypischen Entwurf eines objektorientierten Studien-Dashboards, entwickelt in Python. Das Dashboard dient der Überwachung des individuellen Studienfortschritts (Notendurchschnitt, ECTS-Punkte, Modulstatus).


## Systemvoraussetzungen

Das Dashboard wurde als portabler Prototyp konzipiert. Es werden benötigt:
* Ein Standard-Windows-Betriebssystem.
* Eine installierte Python-Version (empfohlen: Python 3.11 oder neuer).
* **Keine externen Pakete:** Die Anwendung nutzt ausschließlich die Python-Standardbibliothek (`tkinter` für die GUI, `json` für die Persistenz). Eine Internetverbindung zur Laufzeit oder Installation über `pip` ist **nicht** erforderlich.

## Installation & Ausführung

Da das Programm portabel ist, muss es nicht klassisch installiert werden:

1. Klicke oben rechts auf den grünen Button **"<> Code"** und lade das Projekt als ZIP-Datei herunter (oder klone das Repository).
2. Entpacke die Dateien in einen beliebigen Ordner.
3. Führe die Datei `main.py` per Doppelklick aus. 
   *(Alternativ über die Kommandozeile: Navigiere in den Ordner und tippe `python main.py` ein).*

Das Dashboard-Fenster öffnet sich nun automatisch.

## Bedienung

* **Module hinzufügen:** Über den entsprechenden Button können neue Module inkl. Semester, ECTS und Prüfungsart (Klausur, Hausarbeit, Portfolio) angelegt werden.
* **Noten eintragen:** Wähle ein Modul in der Tabelle aus und klicke auf "Note eintragen". Die KPIs (Schnitt & ECTS) aktualisieren sich in Echtzeit.
* **Daten speichern:** Sichert den aktuellen Stand in einer frei wählbaren `.json` Datei auf dem System.