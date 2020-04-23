import curses

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def _addstr(self, y_coord, x_coord, text, color_info):
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height, screen_width = self.stdscr.getmaxyx()
        if x_coord + len(text) == screen_width and y_coord == screen_height-1:
            try:
                self.stdscr.addstr(y_coord, x_coord, text, color_info)
            except curses.error:
                pass
        else:
            self.stdscr.addstr(y_coord, x_coord, text, color_info)

def main(stdscr):
    app = App(stdscr)
    while True:
        try:
            user_input = app.stdscr.getch()
        except curses.error:
            continue

        if user_input == 27: # ESC
            break

if __name__ == "__main__":
    curses.wrapper(main)
