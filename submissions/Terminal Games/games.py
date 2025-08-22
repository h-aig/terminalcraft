import time
import random
import curses
import json
import os
from typing import List, Dict, Tuple, Set

# Check for sound support
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

###########################################
# Typing Speed Test Implementation
###########################################

class TypingSpeedTest:
    def __init__(self):
        self.difficulty_levels = {
            "easy": {
                "sentences": [
                    "The quick brown fox jumps over the lazy dog.",
                    "A journey of a thousand miles begins with a single step.",
                    "All that glitters is not gold.",
                    "The early bird catches the worm.",
                    "Practice makes perfect."
                ],
                "time_limit": 60
            },
            "medium": {
                "sentences": [
                    "The five boxing wizards jump quickly to protect the mayor from zombies.",
                    "Amazingly few discotheques provide jukeboxes to weary travelers.",
                    "How vexingly quick daft zebras jump when playing the xylophone!",
                    "The job requires extra pluck and zeal from every young wage earner.",
                    "We promptly judged antique ivory buckles for the next prize."
                ],
                "time_limit": 45
            },
            "hard": {
                "sentences": [
                    "Sphinx of black quartz, judge my vow! Pack my box with five dozen liquor jugs.",
                    "Crazy Fredrick bought many very exquisite opal jewels and quickly zapped them in big wave.",
                    "The job of waxing linoleum frequently peeves chintzy kids and quibbling zombies.",
                    "Jackdaws love my big sphinx of quartz. Five or six big jet planes zoomed quickly by the tower.",
                    "As quirky joke, chefs won't pay devil magic zebra tax. Few black taxis drive up major roads on quiet hazy nights."
                ],
                "time_limit": 30
            }
        }
        self.current_difficulty = "easy"
        self.stats = {
            "wpm": 0,
            "accuracy": 0,
            "time": 0
        }
        self.high_scores = self.load_high_scores()
        self.sound_enabled = True
    
    def get_random_sentence(self) -> str:
        sentences = self.difficulty_levels[self.current_difficulty]["sentences"]
        return random.choice(sentences)
    
    def calculate_wpm(self, text: str, time_taken: float) -> float:
        words = len(text) / 5
        minutes = time_taken / 60
        return words / minutes if minutes > 0 else 0
    
    def calculate_accuracy(self, original: str, typed: str) -> float:
        if not typed:
            return 0.0
        original_len = len(original)
        typed_len = len(typed)
        matrix = [[0 for _ in range(typed_len + 1)] for _ in range(original_len + 1)]
        for i in range(original_len + 1):
            matrix[i][0] = i
        for j in range(typed_len + 1):
            matrix[0][j] = j
        for i in range(1, original_len + 1):
            for j in range(1, typed_len + 1):
                if original[i-1] == typed[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,
                        matrix[i][j-1] + 1,
                        matrix[i-1][j-1] + 1
                    )
        distance = matrix[original_len][typed_len]
        max_length = max(original_len, typed_len)
        accuracy = (1 - distance / max_length) * 100 if max_length > 0 else 100
        return max(0, accuracy)
    
    def load_high_scores(self) -> Dict:
        default_scores = {
            "easy": {"wpm": 0, "accuracy": 0},
            "medium": {"wpm": 0, "accuracy": 0},
            "hard": {"wpm": 0, "accuracy": 0}
        }
        try:
            if os.path.exists("typing_scores.json"):
                with open("typing_scores.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return default_scores
    
    def save_high_scores(self) -> None:
        try:
            with open("typing_scores.json", "w") as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def play_sound(self, sound_type: str) -> None:
        if not self.sound_enabled or not SOUND_AVAILABLE:
            return
        try:
            if sound_type == "correct":
                winsound.Beep(1000, 50)
            elif sound_type == "wrong":
                winsound.Beep(500, 50)
            elif sound_type == "complete":
                winsound.Beep(1500, 100)
        except:
            pass

    def run_test(self, stdscr) -> Dict:
        curses.curs_set(1)
        stdscr.clear()
        sentence = self.get_random_sentence()
        time_limit = self.difficulty_levels[self.current_difficulty]["time_limit"]
        stdscr.addstr(0, 0, f"Difficulty: {self.current_difficulty.capitalize()} | Time Limit: {time_limit}s")
        stdscr.addstr(2, 0, "Type the following sentence:")
        stdscr.addstr(4, 0, sentence, curses.A_BOLD)
        stdscr.addstr(6, 0, "Your input:")
        stdscr.addstr(8, 0, "Press Esc to quit anytime")
        stdscr.refresh()
        user_input = ""
        start_time = time.time()
        elapsed_time = 0
        input_y, input_x = 7, 0
        stdscr.move(input_y, input_x)
        while elapsed_time < time_limit:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, time_limit - elapsed_time)
            stdscr.addstr(1, 0, f"Time remaining: {remaining_time:.1f}s")
            try:
                key = stdscr.getch()
            except:
                continue
            if key == 27:
                return {"wpm": 0, "accuracy": 0, "time": elapsed_time}
            elif key in (8, 127, curses.KEY_BACKSPACE):
                if user_input:
                    user_input = user_input[:-1]
                    stdscr.addstr(input_y, 0, " " * len(sentence))
                    stdscr.addstr(input_y, 0, user_input)
            elif key in (10, 13):
                break
            elif 32 <= key <= 126:
                user_input += chr(key)
                current_char = chr(key)
                if len(user_input) <= len(sentence):
                    if current_char == sentence[len(user_input)-1]:
                        stdscr.addstr(input_y, len(user_input) - 1, current_char, 
                                    curses.color_pair(1))
                        self.play_sound("correct")
                    else:
                        stdscr.addstr(input_y, len(user_input) - 1, current_char, 
                                    curses.color_pair(2))
                        self.play_sound("wrong")
                if user_input == sentence:
                    self.play_sound("complete")
                    break
            stdscr.refresh()
        final_time = time.time() - start_time
        wpm = self.calculate_wpm(user_input, final_time)
        accuracy = self.calculate_accuracy(sentence, user_input)
        self.stats = {
            "wpm": wpm,
            "accuracy": accuracy,
            "time": final_time
        }
        self.update_high_scores()
        return self.stats
    
    def update_high_scores(self) -> bool:
        current = self.high_scores[self.current_difficulty]
        new_high_score = False
        
        if self.stats["wpm"] > current["wpm"]:
            current["wpm"] = self.stats["wpm"]
            new_high_score = True
        
        if self.stats["accuracy"] > current["accuracy"]:
            current["accuracy"] = self.stats["accuracy"]
            new_high_score = True
        
        if new_high_score:
            self.save_high_scores()
        
        return new_high_score

    def display_results(self, stdscr) -> None:
        stdscr.clear()
        stdscr.addstr(0, 0, "Typing Test Results", curses.A_BOLD)
        stdscr.addstr(2, 0, f"Words Per Minute (WPM): {self.stats['wpm']:.2f}")
        stdscr.addstr(3, 0, f"Accuracy: {self.stats['accuracy']:.2f}%")
        stdscr.addstr(4, 0, f"Time taken: {self.stats['time']:.2f} seconds")
        high_scores = self.high_scores[self.current_difficulty]
        stdscr.addstr(6, 0, f"High Scores for {self.current_difficulty.capitalize()}:", curses.A_BOLD)
        stdscr.addstr(7, 0, f"Best WPM: {high_scores['wpm']:.2f}")
        stdscr.addstr(8, 0, f"Best Accuracy: {high_scores['accuracy']:.2f}%")
        if self.update_high_scores():
            stdscr.addstr(10, 0, "NEW HIGH SCORE!", curses.A_BOLD | curses.A_BLINK)
        if self.stats['wpm'] >= 60 and self.stats['accuracy'] >= 95:
            rating = "Excellent! You're a typing master!"
        elif self.stats['wpm'] >= 40 and self.stats['accuracy'] >= 90:
            rating = "Great job! Your typing skills are solid."
        elif self.stats['wpm'] >= 20 and self.stats['accuracy'] >= 80:
            rating = "Good effort! Keep practicing to improve."
        else:
            rating = "Practice makes perfect. Keep going!"
        stdscr.addstr(12, 0, f"Rating: {rating}")
        stdscr.addstr(14, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()
    
    def select_difficulty(self, stdscr) -> str:
        curses.curs_set(0)
        stdscr.clear()
        difficulties = list(self.difficulty_levels.keys())
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Select Difficulty Level", curses.A_BOLD)
            stdscr.addstr(2, 0, "Enter a number to select difficulty:")
            for i, diff in enumerate(difficulties, 1):
                y = i + 3
                stdscr.addstr(y, 0, f"{i}. {diff.capitalize()}")
            stdscr.refresh()
            try:
                key = stdscr.getch()
                choice = chr(key)
                if choice in "123":
                    selected = int(choice) - 1
                    self.current_difficulty = difficulties[selected]
                    break
            except:
                continue
        return self.current_difficulty
    
    def main_menu(self, stdscr) -> None:
        curses.curs_set(0)
        options = ["Start Typing Test", "Select Difficulty", "View Instructions", 
                  "Toggle Sound", "View High Scores", "Return to Main Menu"]
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Typing Speed Test", curses.A_BOLD)
            stdscr.addstr(1, 0, f"Current Difficulty: {self.current_difficulty.capitalize()}")
            stdscr.addstr(2, 0, f"Sound: {'On' if self.sound_enabled else 'Off'}")
            for i, option in enumerate(options, 1):
                y = i + 3
                stdscr.addstr(y, 0, f"{i}. {option}")
            stdscr.addstr(len(options) + 5, 0, "Enter a number (1-6) to select an option: ")
            stdscr.refresh()
            try:
                key = stdscr.getch()
                choice = chr(key)
                if choice in "123456":
                    selected = int(choice) - 1
                    if selected == 0:
                        self.run_test(stdscr)
                        self.display_results(stdscr)
                    elif selected == 1:
                        self.select_difficulty(stdscr)
                    elif selected == 2:
                        self.show_instructions(stdscr)
                    elif selected == 3:
                        self.sound_enabled = not self.sound_enabled
                    elif selected == 4:
                        self.show_high_scores(stdscr)
                    elif selected == 5:
                        break
            except:
                continue

    def show_instructions(self, stdscr) -> None:
        stdscr.clear()
        stdscr.addstr(0, 0, "Typing Test Instructions", curses.A_BOLD)
        instructions = [
            "1. You will be shown a sentence to type.",
            "2. Type the sentence exactly as shown, including punctuation and capitalization.",
            "3. Your typing speed (WPM) and accuracy will be calculated.",
            "4. Press Enter when you finish typing or wait for the timer to end.",
            "5. Press Esc at any time to quit the current test.",
            "",
            "Difficulty Levels:",
            "- Easy: Simple sentences, 60 seconds time limit",
            "- Medium: More complex sentences, 45 seconds time limit",
            "- Hard: Challenging sentences with punctuation, 30 seconds time limit"
        ]
        for i, line in enumerate(instructions):
            stdscr.addstr(i + 2, 0, line)
        stdscr.addstr(i + 4, 0, "Press any key to return to the main menu...")
        stdscr.refresh()
        stdscr.getch()

    def show_high_scores(self, stdscr) -> None:
        stdscr.clear()
        stdscr.addstr(0, 0, "High Scores", curses.A_BOLD)
        y = 2
        for difficulty in self.difficulty_levels.keys():
            scores = self.high_scores[difficulty]
            stdscr.addstr(y, 0, f"{difficulty.capitalize()}:", curses.A_BOLD)
            stdscr.addstr(y + 1, 2, f"Best WPM: {scores['wpm']:.2f}")
            stdscr.addstr(y + 2, 2, f"Best Accuracy: {scores['accuracy']:.2f}%")
            y += 4
        stdscr.addstr(y + 1, 0, "Press any key to return to main menu...")
        stdscr.refresh()
        stdscr.getch()

    def start(self, stdscr) -> None:
        """Main entry point for typing test"""
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        self.main_menu(stdscr)


###########################################
# Minesweeper Implementation
###########################################

class Minesweeper:
    def __init__(self):
        self.difficulty_levels = {
            'beginner': {'size': 9, 'mines': 10},
            'intermediate': {'size': 16, 'mines': 40},
            'expert': {'size': 22, 'mines': 99}
        }
        self.current_difficulty = 'beginner'
        self.board = []
        self.visible = []
        self.mines_locations = set()
        self.flags = set()
        self.game_over = False
        self.won = False
        self.first_move = True
        self.cursor_x = 0
        self.cursor_y = 0
        self.initialize_game()

    def initialize_game(self) -> None:
        size = self.difficulty_levels[self.current_difficulty]['size']
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.visible = [[False for _ in range(size)] for _ in range(size)]
        self.mines_locations = set()
        self.flags = set()
        self.game_over = False
        self.won = False
        self.first_move = True
        self.cursor_x = 0
        self.cursor_y = 0

    def place_mines(self, first_x: int, first_y: int) -> None:
        size = self.difficulty_levels[self.current_difficulty]['size']
        num_mines = self.difficulty_levels[self.current_difficulty]['mines']
        safe_zone = {(x, y) for x in range(max(0, first_x-1), min(size, first_x+2))
                           for y in range(max(0, first_y-1), min(size, first_y+2))}
        all_positions = {(x, y) for x in range(size) for y in range(size)} - safe_zone
        self.mines_locations = set(random.sample(list(all_positions), num_mines))
        for x, y in self.mines_locations:
            self.board[x][y] = -1
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < size and 0 <= new_y < size and 
                        self.board[new_x][new_y] != -1):
                        self.board[new_x][new_y] += 1

    def reveal(self, x: int, y: int) -> bool:
        size = self.difficulty_levels[self.current_difficulty]['size']
        if not (0 <= x < size and 0 <= y < size) or self.visible[x][y]:
            return True
        if self.first_move:
            self.place_mines(x, y)
            self.first_move = False
        self.visible[x][y] = True
        if self.board[x][y] == -1:
            self.game_over = True
            return False
        if self.board[x][y] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal(x + dx, y + dy)
        return True

    def toggle_flag(self, x: int, y: int) -> None:
        if not self.visible[x][y]:
            pos = (x, y)
            if pos in self.flags:
                self.flags.remove(pos)
            else:
                self.flags.add(pos)

    def check_win(self) -> bool:
        size = self.difficulty_levels[self.current_difficulty]['size']
        for x in range(size):
            for y in range(size):
                if self.board[x][y] != -1 and not self.visible[x][y]:
                    return False
        self.won = True
        return True

    def get_cell_display(self, x: int, y: int, is_cursor: bool) -> str:
        cell = ''
        if (x, y) in self.flags:
            cell = '🚩'
        elif not self.visible[x][y]:
            cell = '■'
        elif self.board[x][y] == -1:
            cell = '💣'
        elif self.board[x][y] == 0:
            cell = '·'
        else:
            cell = str(self.board[x][y])
        if is_cursor:
            return f'[{cell}]'
        return f' {cell} '

    def display_board(self, stdscr) -> None:
        stdscr.clear()
        size = self.difficulty_levels[self.current_difficulty]['size']
        stdscr.addstr(0, 0, "MINESWEEPER", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Difficulty: {self.current_difficulty.capitalize()}")
        stdscr.addstr(3, 4, '  ' + ''.join(f'{i:3}' for i in range(size)))
        stdscr.addstr(4, 2, '  ┌' + '───' * size + '┐')
        for i in range(size):
            stdscr.addstr(i + 5, 0, f'{i:2}')
            stdscr.addstr(i + 5, 2, '│')
            for j in range(size):
                is_cursor = (i == self.cursor_y and j == self.cursor_x)
                cell = self.get_cell_display(i, j, is_cursor)
                screen_y = i + 5
                screen_x = j * 3 + 3
                if is_cursor:
                    stdscr.addstr(screen_y, screen_x, cell, curses.A_REVERSE)
                else:
                    stdscr.addstr(screen_y, screen_x, cell)
            stdscr.addstr(i + 5, size * 3 + 3, '│')
        stdscr.addstr(size + 5, 2, '  └' + '───' * size + '┘')
        status_y = size + 7
        mines_left = len(self.mines_locations) - len(self.flags)
        stdscr.addstr(status_y, 0, f"Mines remaining: {mines_left}")
        if self.game_over:
            stdscr.addstr(status_y + 1, 0, "Game Over! You hit a mine!")
        elif self.won:
            stdscr.addstr(status_y + 1, 0, "Congratulations! You won!")
        stdscr.addstr(status_y + 2, 0, "Controls: WASD to move, Space to reveal, F to flag, Q to quit")
        stdscr.refresh()

    def play(self, stdscr) -> None:
        curses.curs_set(0)
        stdscr.clear()
        size = self.difficulty_levels[self.current_difficulty]['size']
        while True:
            self.display_board(stdscr)
            if self.game_over or self.won:
                stdscr.getch()
                break
            try:
                key = stdscr.getch()
                if key in (ord('w'), ord('W')) and self.cursor_y > 0:
                    self.cursor_y -= 1
                elif key in (ord('s'), ord('S')) and self.cursor_y < size - 1:
                    self.cursor_y += 1
                elif key in (ord('a'), ord('A')) and self.cursor_x > 0:
                    self.cursor_x -= 1
                elif key in (ord('d'), ord('D')) and self.cursor_x < size - 1:
                    self.cursor_x += 1
                elif key == ord(' '):
                    if not self.reveal(self.cursor_y, self.cursor_x):
                        self.display_board(stdscr)
                        stdscr.getch()
                        break
                    self.check_win()
                elif key in (ord('f'), ord('F')):
                    self.toggle_flag(self.cursor_y, self.cursor_x)
                elif key in (ord('q'), ord('Q')):
                    break
            except curses.error:
                continue

    def select_difficulty(self, stdscr) -> None:
        curses.curs_set(1)
        stdscr.clear()
        stdscr.addstr(0, 0, "Select Difficulty:")
        stdscr.addstr(1, 0, "1. Beginner (9x9, 10 mines)")
        stdscr.addstr(2, 0, "2. Intermediate (16x16, 40 mines)")
        stdscr.addstr(3, 0, "3. Expert (22x22, 99 mines)")
        stdscr.addstr(4, 0, "Enter choice (1-3): ")
        stdscr.refresh()
        while True:
            try:
                choice = stdscr.getch()
                if choice in (ord('1'), ord('2'), ord('3')):
                    if choice == ord('1'):
                        self.current_difficulty = 'beginner'
                    elif choice == ord('2'):
                        self.current_difficulty = 'intermediate'
                    else:
                        self.current_difficulty = 'expert'
                    break
            except curses.error:
                continue

    def start(self, stdscr) -> None:
        """Main entry point for minesweeper"""
        while True:
            self.select_difficulty(stdscr)
            self.initialize_game()
            self.play(stdscr)
            
            stdscr.clear()
            stdscr.addstr(0, 0, "Play again? (y/n): ")
            stdscr.refresh()
            
            play_again = False
            while True:
                try:
                    choice = stdscr.getch()
                    if choice in (ord('y'), ord('Y')):
                        play_again = True
                        break
                    elif choice in (ord('n'), ord('N')):
                        play_again = False
                        break
                except curses.error:
                    continue
            
            if not play_again:
                break


###########################################
# Main Program
###########################################

def main_menu(stdscr) -> None:
    """Display the main menu to choose between games"""
    curses.curs_set(0)
    
    # Initialize colors
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "PYTHON GAMES COLLECTION", curses.A_BOLD)
        stdscr.addstr(2, 0, "Select a game to play:")
        stdscr.addstr(4, 0, "1. Typing Speed Test", curses.color_pair(1))
        stdscr.addstr(5, 0, "2. Minesweeper", curses.color_pair(3))
        stdscr.addstr(6, 0, "3. Quit")
        stdscr.addstr(8, 0, "Enter your choice (1-3): ")
        stdscr.refresh()
        
        try:
            key = stdscr.getch()
            if key == ord('1'):
                typing_game = TypingSpeedTest()
                typing_game.start(stdscr)
            elif key == ord('2'):
                mine_game = Minesweeper()
                mine_game.start(stdscr)
            elif key == ord('3'):
                break
        except curses.error:
            continue

def main(stdscr):
    # Set up the screen
    stdscr.clear()
    main_menu(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
