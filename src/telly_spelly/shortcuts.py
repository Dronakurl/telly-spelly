from PyQt6.QtCore import QObject, pyqtSignal
import logging
import dbus
import dbus.service

logger = logging.getLogger(__name__)

DBUS_SERVICE = "org.kde.telly_spelly"
DBUS_PATH = "/TellySpelly"
DBUS_INTERFACE = "org.kde.telly_spelly"


class DBusService(dbus.service.Object):
    """D-Bus service object that receives shortcut triggers from KDE"""

    def __init__(self, bus, path, shortcuts):
        dbus.service.Object.__init__(self, bus, path)
        self.shortcuts = shortcuts

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def StartRecording(self):
        """Start recording - called by KDE when shortcut is pressed"""
        logger.info("D-Bus: StartRecording called")
        self.shortcuts.start_recording_triggered.emit()
        return True

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def StopRecording(self):
        """Stop recording - called by KDE when shortcut is pressed"""
        logger.info("D-Bus: StopRecording called")
        self.shortcuts.stop_recording_triggered.emit()
        return True

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def ToggleRecording(self):
        """Toggle recording - called by KDE when shortcut is pressed"""
        logger.info("D-Bus: ToggleRecording called")
        self.shortcuts.toggle_recording_triggered.emit()
        return True


class GlobalShortcuts(QObject):
    """
    Global Shortcuts integration via D-Bus.

    Shortcuts are configured via the desktop file actions in telly-spelly.desktop.
    KDE reads these actions and allows users to assign shortcuts in System Settings.
    When a shortcut is triggered, KDE runs the dbus-send command which calls our
    D-Bus methods (StartRecording, StopRecording, ToggleRecording).

    This approach persists shortcuts in ~/.config/kglobalshortcutsrc and doesn't
    require user confirmation on each startup.
    """

    start_recording_triggered = pyqtSignal()
    stop_recording_triggered = pyqtSignal()
    toggle_recording_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dbus_service = None
        self.bus_name = None
        self.registered = False
        self.session_bus = None

    def setup_shortcuts(self, start_key='Ctrl+Alt+R', stop_key='Ctrl+Alt+S'):
        """Setup D-Bus service to receive shortcut triggers from KDE"""
        try:
            self.session_bus = dbus.SessionBus()

            # Request the service name (must keep reference!)
            self.bus_name = dbus.service.BusName(DBUS_SERVICE, self.session_bus)

            # Create the service object
            self.dbus_service = DBusService(self.bus_name, DBUS_PATH, self)

            self.registered = True
            logger.info(f"D-Bus service registered: {DBUS_SERVICE}")
            logger.info("Shortcuts are configured via System Settings -> Shortcuts -> Telly Spelly")

            return True

        except Exception as e:
            logger.error(f"Failed to setup D-Bus service: {e}")
            import traceback
            traceback.print_exc()
            return False

    def remove_shortcuts(self):
        """Cleanup"""
        self.registered = False

    def __del__(self):
        self.remove_shortcuts()
