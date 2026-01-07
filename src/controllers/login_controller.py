"""
Login controller - handles login flow logic.
"""
from typing import Callable, Optional
import flet as ft
from network import NetworkClient, LoginStatus
from dialogs.login import LoginDialog


class LoginController:
    """Controller for the login flow."""
    
    def __init__(
        self,
        page: ft.Page,
        network: NetworkClient,
        on_login_success: Callable[[str], None]
    ):
        self.page = page
        self.network = network
        self.on_login_success = on_login_success
        self.pseudo: str = ""
        
        # Create dialog
        self.dialog = LoginDialog(page, on_submit=self._submit)
        
        # Register network callback
        self.network.on_login_response = self._on_response
    
    def show(self):
        """Show the login dialog."""
        self.dialog.show()
    
    def _submit(self, pseudo: str):
        """Called when user submits login form."""
        self.pseudo = pseudo
        self.network.login(pseudo)
    
    def _on_response(self, status: LoginStatus):
        """Called when server responds to login."""
        def update_ui():
            if status == LoginStatus.OK:
                self.dialog.hide()
                self.on_login_success(self.pseudo)
            else:
                self.dialog.show_error("Pseudo refusé (déjà utilisé?)")
        
        self.page.run_thread(update_ui)
    
    def on_disconnected(self):
        """Called when disconnected from server."""
        def update_ui():
            self.dialog.show()
            self.dialog.show_error("Déconnecté du serveur")
        
        self.page.run_thread(update_ui)
