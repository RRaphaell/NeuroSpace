import traceback


def catch_exception(func):
    def inner(self):
        try:
            func(self)
        except Exception as e:
            self.popup_handler.warning_popup(str(type(e).__name__), str(e) + str(traceback.print_exc()))
            return
    return inner
