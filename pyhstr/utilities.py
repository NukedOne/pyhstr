class EntryCounter:
    def __init__(self, app):
        self.value = 0
        self.app = app

    def inc(self, boundary):
        if self.value == boundary - 1:
            self.value = 0
            self.app.page.inc(self.app.user_interface.get_number_of_pages())
        else:
            self.value += 1

    def dec(self, boundary):
        if self.value == 0:
            self.app.page.dec(self.app.user_interface.get_number_of_pages())
            self.value = len(self.app._look_into()[self.app.page.value]) - 1
        else:
            self.value -= 1

class PageCounter:
    def __init__(self):
        self.value = 0

    def inc(self, boundary):
        if self.value == boundary - 1:
            self.value = 0
        else:
            self.value += 1

    def dec(self, boundary):
        if self.value == 0:
            self.value = boundary - 1
        else:
            self.value -= 1

