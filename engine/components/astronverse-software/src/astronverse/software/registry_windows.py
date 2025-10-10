import win32api
import win32con


class WindowsRegistryManager:
    """Windows注册表管理器"""

    def __init__(self, registry_key_path, registry_handle=None, mode="w"):
        if mode == "r":
            access = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
        else:
            access = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
        self.mode = mode
        self.registry_handle = None
        if registry_handle is None:
            registry_handle = win32con.HKEY_CURRENT_USER
        try:
            self.registry_handle = win32api.RegOpenKeyEx(registry_handle, registry_key_path, 0, access)
        except OSError:
            # 可预见错误，没有就创建
            try:
                self.registry_handle = win32api.RegCreateKey(registry_handle, registry_key_path)
            except OSError as error:
                raise OSError(f"RegCreateKey error {error}") from error

    def __getattr__(self, name):
        if name[0] == "_":
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self.__class__(name, self.registry_handle, self.mode)

    def __setattr__(self, name, value):
        if name in ("registry_handle", "mode") or name in self.__dict__:
            self.__dict__[name] = value
            return
        self.__getattr__(name)[""] = value

    def __getitem__(self, name):
        try:
            value, types = win32api.RegQueryValueEx(self.registry_handle, name)
            if types == win32con.REG_MULTI_SZ:
                return tuple(value)
            return value
        except OSError as error:
            raise OSError(f"RegQueryValueEx error {error}") from error

    def __setitem__(self, name, value):
        try:
            if isinstance(value, (tuple, list)):
                value = list(map(str, value))
                win32api.RegSetValueEx(self.registry_handle, name, None, win32con.REG_MULTI_SZ, value)
            elif isinstance(value, bytes):
                win32api.RegSetValueEx(
                    self.registry_handle,
                    name,
                    None,
                    win32con.REG_SZ,
                    value.decode("UTF8"),
                )
            else:
                win32api.RegSetValueEx(self.registry_handle, name, None, win32con.REG_SZ, str(value))
        except OSError as error:
            raise OSError(f"RegSetValueEx error {error}") from error

    def __del__(self):
        if self.registry_handle is not None:
            win32api.RegCloseKey(self.registry_handle)
            self.registry_handle = None
