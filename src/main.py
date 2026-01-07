"""
PyGhost Flet Desktop Client
"""
import flet as ft
from network import NetworkClient
from controllers.login_controller import LoginController


class GhostApp:
    """Main Ghost application."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Ghost"
        self.page.window.width = 800
        self.page.window.height = 600
        
        self.pseudo: str = ""
        self.network = NetworkClient()
        
        # Setup controllers
        self.login_controller = LoginController(
            page=self.page,
            network=self.network,
            on_login_success=self._on_login_success
        )
        
        # Setup remaining network callbacks
        self.network.on_room_list = self._on_room_list
        self.network.on_disconnected = self._on_disconnected
        
        # Build UI
        self._build_ui()
        
        # Start network and show login
        self.network.start()
        self.login_controller.show()
    
    def _build_ui(self):
        """Build the main UI."""
        self.rooms_view = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Rooms list",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "La liste des rooms apparaîtra ici.",
                    size=14,
                    color=ft.Colors.GREY_500
                )
            ]),
            visible=False,
            padding=20
        )
        
        self.page.add(self.rooms_view)
    
    def _on_login_success(self, pseudo: str):
        """Called when login succeeds."""
        self.pseudo = pseudo
        self.rooms_view.visible = True
        self.page.update()
    
    def _on_room_list(self, rooms):
        """Called when room list is received."""
        # Will be implemented later
        pass
    
    def _on_disconnected(self):
        """Called when disconnected from server."""
        self.rooms_view.visible = False
        self.login_controller.on_disconnected()


def main(page: ft.Page):
    GhostApp(page)


if __name__ == '__main__':
    ft.run(main)
