"""
Login dialog for PyGhost.
"""
import flet as ft
from typing import Callable, Optional


class LoginDialog:
    """Login dialog with pseudo input."""
    
    def __init__(self, page: ft.Page, on_submit: Callable[[str], None]):
        self.page = page
        self.on_submit = on_submit
        self._build_dialog()
    
    def _build_dialog(self):
        """Build the login dialog UI."""
        self.pseudo_input = ft.TextField(
            label="Votre pseudo",
            hint_text="Entrez votre pseudo...",
            autofocus=True,
            on_submit=self._handle_submit,
            width=300,
        )
        
        self.error_text = ft.Text(
            value="",
            color=ft.Colors.RED_400,
            size=12,
            visible=False,
        )
        
        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
        )
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Bienvenue dans Ghost!", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Text("Choisissez un pseudo pour rejoindre une partie."),
                    ft.Container(height=10),
                    self.pseudo_input,
                    self.error_text,
                    self.loading,
                ],
                tight=True,
                width=320,
            ),
            actions=[
                ft.TextButton("Valider", on_click=self._handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(self.dialog)
    
    def _handle_submit(self, e):
        """Validate and submit pseudo."""
        pseudo = self.pseudo_input.value.strip()
        
        # Validate
        if not pseudo:
            self.show_error("Le pseudo ne peut pas être vide.")
            return
        
        if len(pseudo) > 20:
            self.show_error("Le pseudo ne peut pas dépasser 20 caractères.")
            return
        
        # Show loading
        self.loading.visible = True
        self.error_text.visible = False
        self.page.update()
        
        # Call submit callback
        self.on_submit(pseudo)
    
    def show(self):
        """Show the dialog."""
        self.dialog.open = True
        self.loading.visible = False
        self.error_text.visible = False
        self.pseudo_input.value = ""
        self.page.update()
    
    def hide(self):
        """Hide the dialog."""
        self.dialog.open = False
        self.loading.visible = False
        self.page.update()
    
    def show_error(self, message: str):
        """Display an error message."""
        self.loading.visible = False
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()