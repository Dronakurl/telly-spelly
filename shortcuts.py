from PyQt6.QtCore import QObject, pyqtSignal
import logging
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

logger = logging.getLogger(__name__)

DBUS_SERVICE = "org.kde.telly_spelly"
DBUS_PATH = "/TellySpelly"
DBUS_INTERFACE = "org.kde.telly_spelly"


class DBusService(dbus.service.Object):
    """D-Bus service object"""

    def __init__(self, bus, path, shortcuts):
        dbus.service.Object.__init__(self, bus, path)
        self.shortcuts = shortcuts

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def StartRecording(self):
        """Start recording"""
        logger.info("D-Bus: StartRecording called")
        self.shortcuts.start_recording_triggered.emit()
        return True

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def StopRecording(self):
        """Stop recording"""
        logger.info("D-Bus: StopRecording called")
        self.shortcuts.stop_recording_triggered.emit()
        return True

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def ToggleRecording(self):
        """Toggle recording"""
        logger.info("D-Bus: ToggleRecording called")
        self.shortcuts.toggle_recording_triggered.emit()
        return True


class GlobalShortcuts(QObject):
    """KDE Global Shortcuts integration via D-Bus"""

    start_recording_triggered = pyqtSignal()
    stop_recording_triggered = pyqtSignal()
    toggle_recording_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dbus_service = None
        self.bus_name = None
        self.registered = False

    def setup_shortcuts(self, start_key='Ctrl+Alt+R', stop_key='Ctrl+Alt+S'):
        """Setup D-Bus service for shortcuts"""
        try:
            # Initialize D-Bus with GLib main loop (compatible with Qt)
            DBusGMainLoop(set_as_default=True)

            session_bus = dbus.SessionBus()

            # Request the service name (must keep reference!)
            self.bus_name = dbus.service.BusName(DBUS_SERVICE, session_bus)

            # Create the service object
            self.dbus_service = DBusService(self.bus_name, DBUS_PATH, self)

            self.registered = True
            logger.info(f"D-Bus service registered: {DBUS_SERVICE}")
            logger.info(f"Test with: dbus-send --session --print-reply --dest={DBUS_SERVICE} {DBUS_PATH} {DBUS_INTERFACE}.ToggleRecording")
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
