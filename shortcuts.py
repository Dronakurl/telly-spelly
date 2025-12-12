from PyQt6.QtCore import QObject, pyqtSignal
import logging
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import secrets

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
    """Global Shortcuts integration via XDG Desktop Portal and D-Bus"""

    start_recording_triggered = pyqtSignal()
    stop_recording_triggered = pyqtSignal()
    toggle_recording_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dbus_service = None
        self.bus_name = None
        self.registered = False
        self.session_bus = None
        self.portal_session = None

    def setup_shortcuts(self, start_key='Ctrl+Alt+R', stop_key='Ctrl+Alt+S'):
        """Setup D-Bus service for shortcuts"""
        try:
            # Initialize D-Bus with GLib main loop (compatible with Qt)
            DBusGMainLoop(set_as_default=True)

            self.session_bus = dbus.SessionBus()

            # Request the service name (must keep reference!)
            self.bus_name = dbus.service.BusName(DBUS_SERVICE, self.session_bus)

            # Create the service object
            self.dbus_service = DBusService(self.bus_name, DBUS_PATH, self)

            self.registered = True
            logger.info(f"D-Bus service registered: {DBUS_SERVICE}")
            logger.info(f"Test with: dbus-send --session --print-reply --dest={DBUS_SERVICE} {DBUS_PATH} {DBUS_INTERFACE}.ToggleRecording")

            # Register with XDG Desktop Portal GlobalShortcuts
            self._register_portal_shortcuts(start_key, stop_key)

            return True

        except Exception as e:
            logger.error(f"Failed to setup D-Bus service: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _register_portal_shortcuts(self, start_key, stop_key):
        """Register shortcuts via XDG Desktop Portal GlobalShortcuts"""
        try:
            portal = self.session_bus.get_object(
                'org.freedesktop.portal.Desktop',
                '/org/freedesktop/portal/desktop'
            )
            shortcuts_iface = dbus.Interface(portal, 'org.freedesktop.portal.GlobalShortcuts')

            # Generate unique token
            token = secrets.token_hex(8)

            # Create session first
            options = {
                'handle_token': token,
                'session_handle_token': f'telly_spelly_{token}'
            }

            # Listen for Response signal before making the call
            self.session_bus.add_signal_receiver(
                self._on_create_session_response,
                signal_name='Response',
                dbus_interface='org.freedesktop.portal.Request',
                path_keyword='path'
            )

            request_path = shortcuts_iface.CreateSession(options)
            logger.info(f"Portal CreateSession requested: {request_path}")

            # Store shortcut keys for later binding
            self._pending_start_key = start_key
            self._pending_stop_key = stop_key

        except dbus.DBusException as e:
            logger.warning(f"Portal shortcuts not available: {e}")
            logger.info("Shortcuts can be configured manually in System Settings -> Shortcuts")
        except Exception as e:
            logger.warning(f"Portal shortcut registration failed: {e}")

    def _on_create_session_response(self, response, results, path=None):
        """Handle CreateSession response"""
        if response != 0:
            logger.warning(f"CreateSession failed with response {response}")
            return

        try:
            session_handle = results.get('session_handle', '')
            if not session_handle:
                logger.warning("No session handle in response")
                return

            self.portal_session = session_handle
            logger.info(f"Portal session created: {session_handle}")

            # Now bind shortcuts
            self._bind_shortcuts()
        except Exception as e:
            logger.error(f"Error handling session response: {e}")

    def _bind_shortcuts(self):
        """Bind shortcuts to the portal session"""
        if not self.portal_session:
            return

        try:
            portal = self.session_bus.get_object(
                'org.freedesktop.portal.Desktop',
                '/org/freedesktop/portal/desktop'
            )
            shortcuts_iface = dbus.Interface(portal, 'org.freedesktop.portal.GlobalShortcuts')

            # Listen for Activated signal
            self.session_bus.add_signal_receiver(
                self._on_shortcut_activated,
                signal_name='Activated',
                dbus_interface='org.freedesktop.portal.GlobalShortcuts'
            )

            # Define shortcuts
            shortcuts = [
                ('toggle_recording', {
                    'description': dbus.String('Toggle voice recording'),
                    'preferred_trigger': dbus.String(self._pending_start_key)
                }),
                ('stop_recording', {
                    'description': dbus.String('Stop voice recording'),
                    'preferred_trigger': dbus.String(self._pending_stop_key)
                })
            ]

            token = secrets.token_hex(8)
            options = {
                'handle_token': token
            }

            request_path = shortcuts_iface.BindShortcuts(
                dbus.ObjectPath(self.portal_session),
                shortcuts,
                '',  # parent_window
                options
            )
            logger.info(f"BindShortcuts requested: {request_path}")

        except Exception as e:
            logger.error(f"Failed to bind shortcuts: {e}")

    def _on_shortcut_activated(self, session_handle, shortcut_id, timestamp, options):
        """Handle shortcut activation from portal"""
        logger.info(f"Portal shortcut activated: {shortcut_id}")

        if shortcut_id == 'toggle_recording':
            self.toggle_recording_triggered.emit()
        elif shortcut_id == 'stop_recording':
            self.stop_recording_triggered.emit()
        elif shortcut_id == 'start_recording':
            self.start_recording_triggered.emit()

    def remove_shortcuts(self):
        """Cleanup"""
        self.registered = False

    def __del__(self):
        self.remove_shortcuts()
