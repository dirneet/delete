import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class EmptyDirFinderApp:
    def __init__(self, master):
        self.master = master
        master.title("Buscador de Carpetas Vacías")

        # Configuración de la interfaz
        self.frame = ttk.Frame(master)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Botón de escaneo
        self.scan_button = ttk.Button(self.frame, text="Escanear Disco C:", command=self.start_scan)
        self.scan_button.pack(pady=5)

        # Lista de carpetas
        self.listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, width=100, height=20)
        self.listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.listbox, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Botón de eliminación
        self.delete_button = ttk.Button(self.frame, text="Eliminar Seleccionadas", command=self.delete_selected)
        self.delete_button.pack(pady=5)

        # Etiqueta de estado
        self.status_label = ttk.Label(self.frame, text="Listo")
        self.status_label.pack(pady=5)

        # Variables de control
        self.queue = queue.Queue()
        self.scan_running = False

    def start_scan(self):
        if not self.scan_running:
            self.scan_running = True
            self.status_label.config(text="Escaneando...")
            self.listbox.delete(0, tk.END)
            threading.Thread(target=self.scan_empty_dirs, daemon=True).start()
            self.master.after(100, self.process_queue)

    def scan_empty_dirs(self):
        def handle_error(error):
            pass  # Ignorar errores de acceso

        for root, dirs, files in os.walk('C:\\', topdown=False, onerror=handle_error):
            try:
                if not dirs and not files:
                    self.queue.put(root)
            except Exception:
                continue
        
        self.queue.put(None)
        self.scan_running = False

    def process_queue(self):
        try:
            while True:
                path = self.queue.get_nowait()
                if path is None:
                    self.status_label.config(text="Escaneo completado")
                    break
                self.listbox.insert(tk.END, path)
        except queue.Empty:
            pass
        
        if self.scan_running:
            self.master.after(100, self.process_queue)

    def delete_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona carpetas para eliminar")
            return
        
        confirm = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar {len(selected)} carpeta(s) seleccionada(s)?"
        )
        
        if not confirm:
            return

        deleted = []
        failed = []
        
        for index in reversed(selected):
            path = self.listbox.get(index)
            try:
                os.rmdir(path)
                self.listbox.delete(index)
                deleted.append(path)
            except OSError as e:
                failed.append(f"{path} - Error: {str(e)}")

        message = []
        if deleted:
            message.append(f"Carptas eliminadas exitosamente: {len(deleted)}")
        if failed:
            message.append("\nFallas al eliminar:")
            message.extend(failed)
        
        messagebox.showinfo("Resultado", "\n".join(message))

def main():
    root = tk.Tk()
    root.geometry("800x600")
    EmptyDirFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
