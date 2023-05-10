import platform


def notify(message, title=None, subtitle=None):
    if platform.system() == 'Darwin':  # macOSの場合
        import pync
        pync.notify(message, title=title, subtitle=subtitle)

    elif platform.system() == 'Windows':  # Windowsの場合
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message)
