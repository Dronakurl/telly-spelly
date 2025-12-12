from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QApplication
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
    Global Shortcuts integration via D-Bus and KGlobalAccel.

    We register our D-Bus service to receive triggers, then use KGlobalAccel
    to register the actual keyboard shortcut that will call our D-Bus method.
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
        """Setup D-Bus service and register shortcut with KGlobalAccel"""
        try:
            self.session_bus = dbus.SessionBus()

            # Request the service name (must keep reference!)
            self.bus_name = dbus.service.BusName(DBUS_SERVICE, self.session_bus)

            # Create the service object
            self.dbus_service = DBusService(self.bus_name, DBUS_PATH, self)

            self.registered = True
            logger.info(f"D-Bus service registered: {DBUS_SERVICE}")

            # Register shortcut with KGlobalAccel
            self._register_kglobalaccel_shortcut()

            return True

        except Exception as e:
            logger.error(f"Failed to setup D-Bus service: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _register_kglobalaccel_shortcut(self):
        """Register shortcut with KGlobalAccel D-Bus service"""
        try:
            kglobalaccel = self.session_bus.get_object(
                'org.kde.kglobalaccel',
                '/kglobalaccel'
            )
            iface = dbus.Interface(kglobalaccel, 'org.kde.KGlobalAccel')

            # Action ID format: [component, context, action, friendly_name]
            action_id = dbus.Array([
                dbus.String("telly-spelly.desktop"),
                dbus.String(""),
                dbus.String("ToggleRecording"),
                dbus.String("Toggle Recording")
            ], signature='s')

            # Register the action first
            iface.doRegister(action_id)

            # Ctrl+Alt+R key code: Ctrl=0x04000000, Alt=0x08000000, R=0x52
            # Combined: 0x0C000052 = 201326674
            key_code = 0x04000000 | 0x08000000 | ord('R')

            # Set the shortcut (flags=0 means don't overwrite if already set by user)
            keys = dbus.Array([dbus.Int32(key_code)], signature='i')
            iface.setShortcut(action_id, keys, dbus.UInt32(0))

            logger.info("Registered Ctrl+Alt+R shortcut with KGlobalAccel")

        except dbus.DBusException as e:
            logger.warning(f"Could not register with KGlobalAccel: {e}")
            logger.info("Shortcut can be configured manually in System Settings -> Shortcuts")
        except Exception as e:
            logger.warning(f"KGlobalAccel registration error: {e}")

    def remove_shortcuts(self):
        """Cleanup"""
        self.registered = False

    def __del__(self):
        self.remove_shortcuts()
