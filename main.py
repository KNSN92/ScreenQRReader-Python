
from Foundation import NSObject, NSBundle, NSURL, NSDate, NSUserDefaults, NSMutableDictionary, NSUserNotification, NSUserNotificationCenter
import AppKit
from PyObjCTools import AppHelper
from quickmachotkey import quickHotKey, mask
from quickmachotkey.constants import kVK_ANSI_1, cmdKey, shiftKey

from utils import *
import validators
import pyperclip

_MENUBAR_ICON = "icon/menubar_icon.svg"
_APP_ICON = "icon/app_icon.svg"

main_app = None

def main():
    global main_app
    app = AppKit.NSApplication.sharedApplication()
    app.activateIgnoringOtherApps_(True)

    main_app = ScreenQRReaderApp.alloc().init()
    main_app._app = app
    app.setDelegate_(main_app)
    get_notification_center().setDelegate_(main_app)

    AppHelper.installMachInterrupt()
    AppHelper.runEventLoop()

class ScreenQRReaderApp(NSObject):

    def __init__(self):
        self.nsstatusitem = None
        self._app = None
        self._menu = None
        self.preferences = None
        self.reading = False

    def applicationDidFinishLaunching_(self, notification):

        self.reading = False

        self.preferences = {}
        self.loadPreferences()

        self._app = AppKit.NSApplication.sharedApplication()

        self._menu = self.genMenu()

        self.nsstatusitem = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(
            AppKit.NSVariableStatusItemLength)
        self.nsstatusitem.setHighlightMode_(True)

        img = AppKit.NSImage.alloc().initByReferencingFile_(_MENUBAR_ICON)
        img.setScalesWhenResized_(True)
        img.setSize_((20, 20))
        self.nsstatusitem.setImage_(img)

        button = self.nsstatusitem.button()
        button.setAction_("menubarClicked:")
        button.sendActionOn_(AppKit.NSEventMaskLeftMouseUp | AppKit.NSEventMaskRightMouseUp)


    def userNotificationCenter_didActivateNotification_(self, notification_center, notification):
        notification_center.removeDeliveredNotification_(notification)
        ns_dict = notification.userInfo()
        if ns_dict is None:
            return
        else:
            qr_content = ns_dict["value"]
            pyperclip.copy(qr_content)

    def loadPreferences(self):
        saved_preferences_open_in_browser = NSUserDefaults.standardUserDefaults().objectForKey_("preference.open_in_browser")
        saved_preferences_enable_capture_hotkey = NSUserDefaults.standardUserDefaults().objectForKey_("preference.enable_capture_hotkey")

        if saved_preferences_open_in_browser is None:
            self.preferences["open_in_browser"] = True
            NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "preference.open_in_browser")
        else:
            self.preferences["open_in_browser"] = bool(saved_preferences_open_in_browser)

        if saved_preferences_enable_capture_hotkey is None:
            self.preferences["enable_capture_hotkey"] = False
            NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "preference.enable_capture_hotkey")
        else:
            self.preferences["enable_capture_hotkey"] = bool(saved_preferences_enable_capture_hotkey)

    def genMenu(self):
        menu = AppKit.NSMenu.alloc().init()

        # captureBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Capture QR", "captureQR:", '')
        captureBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("読み取り", "captureQR:",'')
        captureBtnMenuItem.setKeyEquivalent_("1")
        captureBtnMenuItem.setKeyEquivalentModifierMask_(AppKit.NSEventModifierFlagCommand | AppKit.NSEventModifierFlagShift)
        menu.addItem_(captureBtnMenuItem)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        # preferencesBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Preferences", None, "")
        preferencesBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("設定", None, "")
        preferencesSubMenu = AppKit.NSMenu.alloc().init()

        openInBrowserPreferencesMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            # "Open in browser", "preferenceOpenInBrowserClicked:", "")
            "URLならブラウザで開く", "preferenceOpenInBrowserClicked:", "")
        openInBrowserPreferencesMenuItem.setState_(self.preferences["open_in_browser"])
        preferencesSubMenu.addItem_(openInBrowserPreferencesMenuItem)

        enableHotkeyPreferencesMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            # "Enable capture hotkey ⇧⌘1", "preferenceEnableCaptureHotkeyClicked:", "")
            "ショートカットキー ⇧⌘1 の有効化", "preferenceEnableCaptureHotkeyClicked:", "")
        enableHotkeyPreferencesMenuItem.setState_(self.preferences["enable_capture_hotkey"])
        preferencesSubMenu.addItem_(enableHotkeyPreferencesMenuItem)

        preferencesBtnMenuItem.setSubmenu_(preferencesSubMenu)
        menu.addItem_(preferencesBtnMenuItem)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        # quitBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "quitApp:", 'q')
        quitBtnMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("終了", "quitApp:", 'q')
        menu.addItem_(quitBtnMenuItem)

        return menu

    def captureQR_(self, sender):
        if self.reading:
            return
        self.reading = True
        try:
            qrcontent, status = capture_qr()
            if status == CaptureQRResponse.STATUS_SUCCESS:
                # qrcontent = qrcontent.encode('ascii').decode('unicode-escape')
                if self.preferences["open_in_browser"] and validators.url(qrcontent.strip(), strict_query=False):
                    open_success = AppKit.NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_(qrcontent.strip()))
                    if open_success: return
                # notify("QRCode is captured successfully!", "Click to copy it to the clipboard.", qrcontent, data=qrcontent)
                notify("QRコードの読み取りに成功しました！", "この通知をクリックしてコピー。", qrcontent, data=qrcontent)
            elif status == CaptureQRResponse.STATUS_CANCEL_CAPTURE: pass
            else:
                # notify("QRCode didn't capture.")
                notify("QRコードの読み取りに失敗しました。")
        finally:
            self.reading = False

    def quitApp_(self, sender):
        self._app.terminate_(sender)

    def menubarClicked_(self, sender):
        event = self._app.currentEvent()
        if event is None: return
        if event.type() == AppKit.NSEventTypeLeftMouseUp: # left click
            self.captureQR_(None)
        elif event.type() == AppKit.NSEventTypeRightMouseUp: # right click
            self.nsstatusitem.setMenu_(self._menu)
            self.nsstatusitem.button().performClick_(None)
            self.nsstatusitem.setMenu_(None)

    def preferenceOpenInBrowserClicked_(self, sender):
        sender.setState_(not sender.state())
        self.preferences["open_in_browser"] = sender.state()
        NSUserDefaults.standardUserDefaults().setBool_forKey_(self.preferences["open_in_browser"], "preference.open_in_browser")

    def preferenceEnableCaptureHotkeyClicked_(self, sender):
        sender.setState_(not sender.state())
        self.preferences["enable_capture_hotkey"] = sender.state()
        NSUserDefaults.standardUserDefaults().setBool_forKey_(self.preferences["enable_capture_hotkey"], "preference.enable_capture_hotkey")

@quickHotKey(virtualKey=kVK_ANSI_1, modifierMask=mask(cmdKey, shiftKey))
def hotkeyPressed():
    if main_app.preferences["enable_capture_hotkey"]: main_app.captureQR_(None)

def get_notification_center():
    notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
    if notification_center is None:
        raise RuntimeError("Failed to setup notification center.")
    return notification_center

def notify(title, subtitle=None, message=None, data=None):
    notification = NSUserNotification.alloc().init()
    notification.set_showsButtons_(False)
    notification.setTitle_(title)
    if subtitle is not None:
        notification.setSubtitle_(subtitle)
    if message is not None:
        notification.setInformativeText_(message)
    if data is not None:
        app = AppKit.NSApplication.sharedApplication()
        ns_dict = NSMutableDictionary.alloc().init()
        ns_dict.setDictionary_({"value": data})
        notification.setUserInfo_(ns_dict)

    notification.setDeliveryDate_(NSDate.dateWithTimeInterval_sinceDate_(0, NSDate.date()))

    notification_center = get_notification_center()
    notification_center.scheduleNotification_(notification)

if __name__ == '__main__':
    main()