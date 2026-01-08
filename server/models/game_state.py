import os

class GameState:
    def __init__(self):
        self.frag = ""
        self.players = [] # List of pseudos
        self.scores = {} # pseudo -> letters (e.g. "G", "GH")
        self.current_player_idx = 0
        self.dictionary = self.load_dictionary()

    def load_dictionary(self):
        try:
            # Construct absolute path to common/words.txt
            current_dir = os.path.dirname(os.path.abspath(__file__))
            words_path = os.path.join(current_dir, "..", "..", "common", "words.txt")
            
            with open(words_path, "r", encoding="utf-8") as f:
                # Read all lines, strip whitespace, and convert to uppercase
                words = {line.strip().upper() for line in f if line.strip()}
            
            print(f"Dictionary loaded: {len(words)} words.")
            return words
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            # Fallback to a small set if file fails
            return {
            "BONJOUR", "MONDE", "PYTHON", "RESEAU", "SOCKET", "GHOST", "TEST",
            "MANGER", "TABLE", "CHAISE", "MAISON", "APPLE", "BANANA", "ORANGE"
        }

    def add_player(self, pseudo):
        if pseudo not in self.players:
            self.players.append(pseudo)
            self.scores[pseudo] = ""
   
    def remove_player(self, pseudo):
        if pseudo in self.players:
            # Need to handle turn if current player leaves
            idx = self.players.index(pseudo)
            if idx < self.current_player_idx:
                self.current_player_idx -= 1
            self.players.remove(pseudo)
            del self.scores[pseudo]
            if self.current_player_idx >= len(self.players):
                self.current_player_idx = 0

    def get_current_player(self):
        if not self.players:
            return None
        return self.players[self.current_player_idx]

    def next_turn(self):
        if not self.players:
            return
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def play_letter(self, letter):
        self.frag += letter.upper()
        
        # Rule 1: If completes a valid word > 3 letters -> LOSE
        if len(self.frag) > 3 and self.frag in self.dictionary:
            return "LOSE_WORD"
            
        # Rule 2: If the fragment is NOT a valid prefix (no word starts with it) -> LOSE
        # (This replaces the manual challenge)
        is_valid_prefix = any(w.startswith(self.frag) for w in self.dictionary)
        if not is_valid_prefix:
            return "LOSE_INVALID"
            
        return "CONTINUE"

    def punish_player(self, pseudo):
        # Add a letter G-H-O-S-T
        if pseudo not in self.scores:
            return
        
        current = self.scores[pseudo]
        ghost = "GHOST"
        if len(current) < 5:
            self.scores[pseudo] += ghost[len(current)]
        
        # Reset fragment
        self.frag = ""
        
        if len(self.scores[pseudo]) >= 5:
            return "ELIMINATED"
        return "PUNISHED"
