"""
Ventana principal de la aplicación desktop.
Interfaz con Tkinter para gestión de reservas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, init_db
from database.models import ReservationStatus
from services.reservation_service import ReservationService
from services.notification_service import NotificationService


class MainWindow:
    """
    Ventana principal de la aplicación.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Reservas")
        self.root.geometry("1200x700")
        
        # Inicializar base de datos
        init_db()
        self.db = SessionLocal()
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Actualizar notificaciones cada 5 segundos
        self.update_notifications()
        
    def setup_styles(self):
        """Configurar estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.danger_color = "#f44336"
        self.warning_color = "#FF9800"
        
        self.root.configure(bg=self.bg_color)
        
    def create_menu(self):
        """Crear barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Actualizar", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="A Reservar", command=lambda: self.show_panel("pending"))
        view_menu.add_command(label="Reservado", command=lambda: self.show_panel("confirmed"))
        view_menu.add_command(label="Historial", command=lambda: self.show_panel("history"))
        
    def create_header(self):
        """Crear encabezado con título y notificaciones"""
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="📋 Sistema de Gestión de Reservas",
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Campana de notificaciones
        self.notification_frame = tk.Frame(header_frame, bg=self.primary_color)
        self.notification_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.notification_button = tk.Button(
            self.notification_frame,
            text="🔔",
            font=("Arial", 24),
            bg=self.primary_color,
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.show_notifications
        )
        self.notification_button.pack()
        
        # Contador de notificaciones
        self.notification_badge = tk.Label(
            self.notification_frame,
            text="",
            font=("Arial", 10, "bold"),
            bg="red",
            fg="white",
            width=3,
            height=1
        )
        # El badge se mostrará solo si hay notificaciones
        
    def create_main_content(self):
        """Crear contenido principal con pestañas"""
        # Frame contenedor
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña "A Reservar"
        self.pending_frame = self.create_reservations_panel("pending")
        self.notebook.add(self.pending_frame, text="📝 A Reservar")
        
        # Pestaña "Reservado"
        self.confirmed_frame = self.create_reservations_panel("confirmed")
        self.notebook.add(self.confirmed_frame, text="✅ Reservado")
        
        # Pestaña "Historial"
        self.history_frame = self.create_reservations_panel("history")
        self.notebook.add(self.history_frame, text="📚 Historial")
        
    def create_reservations_panel(self, panel_type):
        """
        Crear panel de reservas.
        """
        frame = tk.Frame(self.notebook, bg="white")
        
        # Treeview para mostrar reservas
        columns = ("ID", "Plataforma", "Cliente", "Fecha", "Hora", "Personas", "Estado")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Plataforma", text="Plataforma")
        tree.heading("Cliente", text="Cliente")
        tree.heading("Fecha", text="Fecha")
        tree.heading("Hora", text="Hora")
        tree.heading("Personas", text="Personas")
        tree.heading("Estado", text="Estado")
        
        tree.column("ID", width=50)
        tree.column("Plataforma", width=100)
        tree.column("Cliente", width=200)
        tree.column("Fecha", width=120)
        tree.column("Hora", width=80)
        tree.column("Personas", width=80)
        tree.column("Estado", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Botones de acción (solo para panel "pending")
        if panel_type == "pending":
            button_frame = tk.Frame(frame, bg="white")
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            accept_btn = tk.Button(
                button_frame,
                text="✅ Aceptar Reserva",
                bg=self.success_color,
                fg="white",
                font=("Arial", 12, "bold"),
                cursor="hand2",
                command=lambda: self.accept_reservation(tree)
            )
            accept_btn.pack(side=tk.LEFT, padx=5)
            
            reject_btn = tk.Button(
                button_frame,
                text="❌ Rechazar Reserva",
                bg=self.danger_color,
                fg="white",
                font=("Arial", 12, "bold"),
                cursor="hand2",
                command=lambda: self.reject_reservation(tree)
            )
            reject_btn.pack(side=tk.LEFT, padx=5)
        
        # Guardar referencia al tree
        setattr(self, f"{panel_type}_tree", tree)
        
        return frame
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_frame = tk.Frame(self.root, bg="#333", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Listo",
            bg="#333",
            fg="white",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
    def load_reservations(self, panel_type):
        """
        Cargar reservas en el panel correspondiente.
        """
        tree = getattr(self, f"{panel_type}_tree")
        
        # Limpiar tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Obtener reservas según el tipo
        if panel_type == "pending":
            reservations = ReservationService.get_pending_reservations(self.db)
        elif panel_type == "confirmed":
            reservations = ReservationService.get_confirmed_reservations(self.db)
        else:  # history
            reservations = ReservationService.get_all_reservations(self.db)
        
        # Insertar reservas en el tree
        for res in reservations:
            date_str = res.reservation_date.strftime("%d/%m/%Y") if res.reservation_date else "N/A"
            time_str = res.reservation_time or "N/A"
            party_size_str = str(res.party_size) if res.party_size else "N/A"
            
            tree.insert("", tk.END, values=(
                res.id,
                res.platform.value,
                res.customer_name or res.customer_id,
                date_str,
                time_str,
                party_size_str,
                res.status.value
            ))
    
    def accept_reservation(self, tree):
        """Aceptar una reserva seleccionada"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una reserva primero")
            return
        
        item = tree.item(selected[0])
        reservation_id = item['values'][0]
        
        # Confirmar acción
        if messagebox.askyesno("Confirmar", "¿Aceptar esta reserva?"):
            ReservationService.update_reservation_status(
                self.db,
                reservation_id,
                ReservationStatus.CONFIRMED
            )
            
            self.status_label.config(text=f"Reserva #{reservation_id} aceptada")
            self.refresh_data()
            messagebox.showinfo("Éxito", "Reserva aceptada correctamente")
    
    def reject_reservation(self, tree):
        """Rechazar una reserva seleccionada"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una reserva primero")
            return
        
        item = tree.item(selected[0])
        reservation_id = item['values'][0]
        
        # Confirmar acción
        if messagebox.askyesno("Confirmar", "¿Rechazar esta reserva?"):
            ReservationService.update_reservation_status(
                self.db,
                reservation_id,
                ReservationStatus.REJECTED
            )
            
            self.status_label.config(text=f"Reserva #{reservation_id} rechazada")
            self.refresh_data()
            messagebox.showinfo("Éxito", "Reserva rechazada correctamente")
    
    def show_notifications(self):
        """Mostrar ventana de notificaciones"""
        notifications = NotificationService.get_unread_notifications(self.db)
        
        if not notifications:
            messagebox.showinfo("Notificaciones", "No hay notificaciones nuevas")
            return
        
        # Crear ventana de notificaciones
        notif_window = tk.Toplevel(self.root)
        notif_window.title("Notificaciones")
        notif_window.geometry("500x400")
        
        # Lista de notificaciones
        listbox = tk.Listbox(notif_window, font=("Arial", 11))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for notif in notifications:
            listbox.insert(tk.END, f"[{notif.created_at.strftime('%H:%M')}] {notif.message}")
        
        # Botón marcar como leídas
        mark_read_btn = tk.Button(
            notif_window,
            text="Marcar todas como leídas",
            command=lambda: self.mark_all_read(notif_window)
        )
        mark_read_btn.pack(pady=10)
    
    def mark_all_read(self, window):
        """Marcar todas las notificaciones como leídas"""
        NotificationService.mark_all_as_read(self.db)
        self.update_notifications()
        window.destroy()
        messagebox.showinfo("Éxito", "Notificaciones marcadas como leídas")
    
    def update_notifications(self):
        """Actualizar contador de notificaciones"""
        count = NotificationService.get_unread_count(self.db)
        
        if count > 0:
            self.notification_badge.config(text=str(count))
            self.notification_badge.pack()
        else:
            self.notification_badge.pack_forget()
        
        # Programar próxima actualización
        self.root.after(5000, self.update_notifications)
    
    def refresh_data(self):
        """Refrescar datos de todos los paneles"""
        self.load_reservations("pending")
        self.load_reservations("confirmed")
        self.load_reservations("history")
        self.status_label.config(text="Datos actualizados")
    
    def show_panel(self, panel_type):
        """Cambiar a un panel específico"""
        panels = {"pending": 0, "confirmed": 1, "history": 2}
        self.notebook.select(panels.get(panel_type, 0))
    
    def on_closing(self):
        """Cerrar aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            self.db.close()
            self.root.destroy()
    
    def run(self):
        """Iniciar la aplicación"""
        # Cargar datos iniciales
        self.refresh_data()
        
        # Configurar evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar loop
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
