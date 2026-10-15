#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#  kitty.py — v4.6.0
#  Same-folder Module.dll · old-version injection · multi-version launcher
#  Auto-offset sync · executor feature config · legacy fallback injectors
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import base64, ctypes, ctypes.wintypes, json, mimetypes, os, platform, re, shutil, socket, struct, subprocess, sys, threading, time, urllib.parse, urllib.request, webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import webview
    HAS_PYWEBVIEW = True
except ImportError:
    webview = None; HAS_PYWEBVIEW = False
try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    Image = ImageDraw = None; HAS_PIL = False
try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    pystray = None; HAS_PYSTRAY = False
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None; HAS_PSUTIL = False

APP_NAME = "Kitty"
APP_VERSION = "4.6.0"
APP_BUILD = "2026.10.15-r2"

APP_DIR = Path.home() / ".kitty_ide"
CONFIG_DIR = APP_DIR / "config"
THEMES_DIR = APP_DIR / "themes"
SCRIPTS_DIR = APP_DIR / "scripts"
AUTOEXEC_DIR = APP_DIR / "autoexec"
CACHE_DIR = APP_DIR / "cache"
PROFILE_DIR = APP_DIR / "profile"
AVATAR_FILE = PROFILE_DIR / "avatar.png"
RECOVERY_FILE = CACHE_DIR / "unsaved_recovery.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

for _folder in (APP_DIR, CONFIG_DIR, THEMES_DIR, SCRIPTS_DIR, AUTOEXEC_DIR, CACHE_DIR, PROFILE_DIR):
    try: _folder.mkdir(parents=True, exist_ok=True)
    except Exception: pass

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_SCRIPT_EXTS = {".lua", ".luau", ".txt"}
DLL_NAME = "Module.dll"
EXEC_HOST = "127.0.0.1"
EXEC_PORT = 6969


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE.DLL DISCOVERY — looks in the same folder as kitty.py first
# ═══════════════════════════════════════════════════════════════════════════════

def _runtime_dir() -> Path:
    try:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent
    except Exception:
        return Path.cwd()

APP_RUNTIME_DIR = _runtime_dir()

DLL_SEARCH_PATHS: List[Path] = [
    APP_RUNTIME_DIR / DLL_NAME,
    APP_RUNTIME_DIR / "bin" / DLL_NAME,
    APP_RUNTIME_DIR / "module" / DLL_NAME,
    APP_RUNTIME_DIR / "modules" / DLL_NAME,
    APP_RUNTIME_DIR.parent / DLL_NAME,
    Path.cwd() / DLL_NAME,
    APP_DIR / "module" / DLL_NAME,
]


def _resolve_dll() -> Optional[Path]:
    for p in DLL_SEARCH_PATHS:
        try:
            if p.is_file():
                return p
        except Exception:
            continue
    return None


def _module_dir() -> Path:
    found = _resolve_dll()
    if found:
        return found.parent
    APP_DIR.joinpath("module").mkdir(parents=True, exist_ok=True)
    return APP_DIR / "module"


# ═══════════════════════════════════════════════════════════════════════════════
#  THEMES + DEFAULTS (condensed)
# ═══════════════════════════════════════════════════════════════════════════════

BUILTIN_THEMES: Dict[str, Dict[str, str]] = {
    "kitty": {"id":"kitty","name":"Kitty","desc":"Paper & ink","bg":"#f4ede1","panel":"#eae2d2","surface":"#ddd3bf","elevated":"#cfc4ad","hover":"#c3b69b","border":"#d6cbb6","borderStrong":"#b3a586","text":"#141419","text2":"#41414d","text3":"#7a7a88","accent":"#1e3a5f","accent2":"#2f5f92","glow":"rgba(30,58,95,0.20)","selection":"rgba(30,58,95,0.22)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-ink": {"id":"kitty-ink","name":"Kitty Ink","desc":"Cream + black ink","bg":"#efe9df","panel":"#e5ded1","surface":"#d6cebf","elevated":"#c5bcab","hover":"#b5ab98","border":"#cec4b2","borderStrong":"#9e9180","text":"#0d0d10","text2":"#36363c","text3":"#6e6e75","accent":"#0d0d10","accent2":"#2a2a30","glow":"rgba(13,13,16,0.18)","selection":"rgba(13,13,16,0.20)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-navy": {"id":"kitty-navy","name":"Kitty Navy","desc":"Ink-navy cat on cream","bg":"#f1eadc","panel":"#e6decb","surface":"#d6cdb6","elevated":"#c4b99e","hover":"#b2a688","border":"#cfc4ab","borderStrong":"#8a7d63","text":"#131824","text2":"#3a4256","text3":"#767c8d","accent":"#1e3a5f","accent2":"#3a6ea5","glow":"rgba(30,58,95,0.22)","selection":"rgba(30,58,95,0.24)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-pink": {"id":"kitty-pink","name":"Kitty Pink","desc":"Grumpy cat","bg":"#f3ebde","panel":"#e8dfce","surface":"#d9cdb6","elevated":"#c8b89c","hover":"#b8a583","border":"#d2c6af","borderStrong":"#8f7f60","text":"#16161a","text2":"#423d42","text3":"#7c7178","accent":"#d97f9a","accent2":"#e898b0","glow":"rgba(217,127,154,0.26)","selection":"rgba(217,127,154,0.28)","success":"#2d8659","warn":"#b87333","danger":"#c4425e"},
    "photo-neon": {"id":"photo-neon","name":"Neon Vibe","desc":"Purple + cyan night","bg":"#0a0814","panel":"#120d24","surface":"#1a1235","elevated":"#251a4a","hover":"#32235f","border":"#2b1f52","borderStrong":"#43307a","text":"#ece5ff","text2":"#a08fd6","text3":"#685b98","accent":"#b388ff","accent2":"#22d3ee","glow":"rgba(179,136,255,0.42)","selection":"rgba(179,136,255,0.34)","success":"#22d3ee","warn":"#fb923c","danger":"#f43f5e"},
    "photo-amber": {"id":"photo-amber","name":"Amber Exit","desc":"Christmas night","bg":"#0f0612","panel":"#1a0c1f","surface":"#25132c","elevated":"#301a38","hover":"#3e234a","border":"#3a2044","borderStrong":"#5a3268","text":"#f4e5ec","text2":"#b894a3","text3":"#7c5f6e","accent":"#e63e3e","accent2":"#fb923c","glow":"rgba(230,62,62,0.38)","selection":"rgba(230,62,62,0.30)","success":"#4ade80","warn":"#fbbf24","danger":"#e63e3e"},
    "photo-fire": {"id":"photo-fire","name":"Purple Fire","desc":"Avatar fire","bg":"#06060c","panel":"#0e0c1a","surface":"#15122a","elevated":"#1e1a3c","hover":"#2a2452","border":"#241e48","borderStrong":"#3c3272","text":"#e8e6ff","text2":"#9188c8","text3":"#5a5388","accent":"#7c3aed","accent2":"#a78bfa","glow":"rgba(124,58,237,0.50)","selection":"rgba(124,58,237,0.38)","success":"#34d399","warn":"#fbbf24","danger":"#ef4444"},
    "reaper": {"id":"reaper","name":"Reaper","desc":"Void + acid green","bg":"#05060a","panel":"#0a0d14","surface":"#101520","elevated":"#161d2c","hover":"#1e2638","border":"#1a2233","borderStrong":"#2a3650","text":"#d8e0f0","text2":"#7c8aa8","text3":"#4a5468","accent":"#6ee7b7","accent2":"#34d399","glow":"rgba(110,231,183,0.42)","selection":"rgba(110,231,183,0.28)","success":"#6ee7b7","warn":"#fcd34d","danger":"#f87171"},
    "void-green": {"id":"void-green","name":"Void Green","desc":"Spectral green","bg":"#050806","panel":"#0a100d","surface":"#101a13","elevated":"#16231a","hover":"#1d3022","border":"#1d3826","borderStrong":"#2d5b3b","text":"#e4f8e9","text2":"#a2c5ac","text3":"#65826d","accent":"#52ff8a","accent2":"#18c964","glow":"rgba(82,255,138,0.32)","selection":"rgba(82,255,138,0.24)","success":"#52ff8a","warn":"#f6d365","danger":"#ff647c"},
    "void-mono": {"id":"void-mono","name":"Void Mono","desc":"Black glass + white","bg":"#050505","panel":"#0c0c0c","surface":"#141414","elevated":"#1b1b1b","hover":"#252525","border":"#292929","borderStrong":"#454545","text":"#f5f5f5","text2":"#c2c2c2","text3":"#777777","accent":"#f5f5f5","accent2":"#bdbdbd","glow":"rgba(245,245,245,0.22)","selection":"rgba(245,245,245,0.20)","success":"#b4f4c0","warn":"#ffd479","danger":"#ff7474"},
    "crimson": {"id":"crimson","name":"Crimson","desc":"Real Executor signature","bg":"#0b0a0d","panel":"#111015","surface":"#17151b","elevated":"#1d1a21","hover":"#252028","border":"#2a2630","borderStrong":"#3a3440","text":"#f0eaf0","text2":"#a094a0","text3":"#6a5f6c","accent":"#c9303d","accent2":"#e8455a","glow":"rgba(201,48,61,0.22)","selection":"rgba(201,48,61,0.24)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
    "graphite": {"id":"graphite","name":"Graphite","desc":"Neutral dev-tool","bg":"#0b0d12","panel":"#11141b","surface":"#171b24","elevated":"#1c2230","hover":"#242c3a","border":"#292f3c","borderStrong":"#3a4254","text":"#f0f3f8","text2":"#a0a9b8","text3":"#737e90","accent":"#8b7cff","accent2":"#60a5fa","glow":"rgba(139,124,255,0.22)","selection":"rgba(139,124,255,0.24)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
    "mono": {"id":"mono","name":"Mono","desc":"Grayscale","bg":"#0f0f0f","panel":"#141414","surface":"#1a1a1a","elevated":"#212121","hover":"#282828","border":"#262626","borderStrong":"#363636","text":"#ededed","text2":"#9a9a9a","text3":"#636363","accent":"#d4d4d4","accent2":"#8f8f8f","glow":"rgba(212,212,212,0.14)","selection":"rgba(212,212,212,0.20)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
}

SECTION_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "appearance": {
        "theme":"kitty","activeLogo":"paw","customAccentHex":"",
        "uiDensity":"compact","cornerRadius":"subtle","sidebarIconSize":14,"sidebarLabels":True,
        "glowIntensity":25,"topoHeaderPattern":True,
        "borderEnabled":True,"borderMode":"rainbow","borderColor":"#b388ff","borderWidth":2,
        "useBackgroundImage":False,"bgImageOpacity":40,"bgImageBlur":4,"bgImageSaturation":100,
        "bgImagePosition":"cover-center","bgScope":"whole","panelOpacity":82,
        "imageAutoTheme":True,"themeBeforeImage":"kitty",
        "customColors":{"bg":"#0b0d12","panel":"#11141b","surface":"#171b24","border":"#292f3c","text":"#f0f3f8","text2":"#a0a9b8","accent":"#8b7cff","accent2":"#60a5fa"},
        "fxType":"orbs","fxIntensity":"med","fxColorMode":"theme","fxColor1":"#1e3a5f","fxColor2":"#2f5f92","fxOpacity":"normal",
        "customTheme":{"name":"Custom Image","imageFilename":"","imageDataUrl":"","palette":dict(BUILTIN_THEMES["kitty"])},
    },
    "roblox": {
        "autoAttach":False,"autoLaunch":False,"autoInject":False,
        "skipVersionCheck":True,"forceOldVersionBypass":True,"preferSuspendedInject":True,
        "patchClientVersion":True,"useManualMapper":False,
        "launchMode":"latest",       # latest | selected
        "selectedVersion":"",
        "injectTimeoutSec":60,
        "raknet":False,"internalUI":False,"bypassAFK":True,
        "execHost":"127.0.0.1","execPort":6969,
    },
    "effects": {
        "masterAnimations":True,"animationSpeed":"normal","hoverEffects":True,"magneticIcons":True,
        "cursorSpotlight":False,"glowEffects":True,"buttonPressAnim":True,"smoothTabTransitions":True,
        "toastAnimations":True,"reduceMotion":False,"ripplesEnabled":True,"staggerEnabled":True,
        "clickParticles":False,"particleColor":"","cursorTrail":False,
        "smoothScrolling":True,"waterCursor":True,"waterIntensity":5,"waterSize":76,
        "particleCount":16,"trailIntervalMs":42,"fogGlow":True,
    },
    "editor": {"fontFamily":"Cascadia Code","fontSize":13,"fontWeight":"400","lineHeight":1.55,"lineNumbers":True,"highlightCurrentLine":True,"indentationGuides":True,"wordWrap":False,"autoIndent":True,"minimap":False,"syntaxTheme":"crimson","tabSize":4,"insertSpaces":True,"autoCloseBrackets":True,"showWhitespace":False,"confirmCloseUnsaved":True},
    "console": {"showConsole":True,"consolePosition":"bottom","consoleHeight":160,"autoScroll":True,"timestamps":True,"filter":"all","maxLines":2000,"confirmClearOutput":False,"rightSidebarVisible":True,"leftExplorerVisible":True,"activityRailVisible":True,"lastActivity":"explorer"},
    "shortcuts": {"save":"Ctrl+S","newTab":"Ctrl+N","closeTab":"Ctrl+W","reopenClosedTab":"Ctrl+Shift+T","find":"Ctrl+F","replace":"Ctrl+H","commandPalette":"Ctrl+K","toggleConsole":"Ctrl+J"},
    "general": {"launchMaximized":False,"minimizeToTray":False,"streamproof":False,"disguiseMode":False,"performanceMode":"medium","globalToggleKey":"Insert","userName":"lostinthoughts","planName":"Free","licenseStatus":"Active","licenseExpires":"Never","defaultNewTabBehavior":"luau_template"},
    "secret": {"unlocked":False,"reaperMode":False},
}

def get_flat_defaults(): return json.loads(json.dumps(SECTION_DEFAULTS))

DEFAULT_SCRIPTS = [
    {"id":"script_save","title":"saveinstance.luau","folder":"Scripts","content":"saveinstance()\n"},
    {"id":"script_actor","title":"Actor Comm Channel.luau","folder":"Scripts","content":"-- Actor channel\nlocal id, ch = create_comm_channel()\n"},
    {"id":"script_ue","title":"UE Counter.luau","folder":"Scripts","content":"-- UE Counter\n"},
    {"id":"script_autoexec_fps","title":"FrameCap.luau","folder":"AutoExec","content":"setfpscap(144)\n"},
]

# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOWS UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

_main_window: Any = None
_tray_icon: Any = None
_main_hidden: bool = False
_hk_thread: Optional[threading.Thread] = None
_hk_stop = threading.Event()

VK_MAP = {"Insert":0x2D,"Delete":0x2E,"Home":0x24,"End":0x23,"PageUp":0x21,"PageDown":0x22,
          "F1":0x70,"F2":0x71,"F3":0x72,"F4":0x73,"F5":0x74,"F6":0x75,"F7":0x76,"F8":0x77,
          "F9":0x78,"F10":0x79,"F11":0x7A,"F12":0x7B}
WM_HOTKEY = 0x0312; WM_QUIT = 0x0012; MOD_NOREPEAT = 0x4000; _HK_ID = 0x4B54

# Win32 constants for injection
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40
CREATE_SUSPENDED = 0x00000004
CREATE_NEW_CONSOLE = 0x00000010
INFINITE = 0xFFFFFFFF


def atomic_write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path); return True
    except Exception:
        return False


def _open_process(pid: int, access: int = PROCESS_ALL_ACCESS):
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = ctypes.wintypes.HANDLE
    k32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    return k32.OpenProcess(access, False, pid)


def _get_pid_version(pid: int) -> Optional[str]:
    try:
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = ctypes.wintypes.HANDLE
        k32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
        k32.QueryFullProcessImageNameW.restype = ctypes.wintypes.BOOL
        k32.QueryFullProcessImageNameW.argtypes = [
            ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD,
            ctypes.wintypes.LPWSTR, ctypes.POINTER(ctypes.wintypes.DWORD)]
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return None
        try:
            size = ctypes.wintypes.DWORD(32768)
            buf = ctypes.create_unicode_buffer(size.value)
            if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                p = buf.value
                v = os.path.basename(os.path.dirname(p))
                if v.lower().startswith("version-"):
                    return v
        finally:
            k32.CloseHandle(h)
    except Exception:
        pass
    return None


def apply_streamproof_win32(enable: bool) -> bool:
    if os.name != "nt" or _main_window is None: return False
    try:
        u32 = ctypes.windll.user32
        flag = 0x00000011 if enable else 0x00000000
        hwnd = getattr(_main_window, "native_handle", None)
        if hwnd:
            return bool(u32.SetWindowDisplayAffinity(ctypes.wintypes.HWND(hwnd), flag))
    except Exception:
        pass
    return False


def apply_process_priority_win32(mode: str) -> bool:
    if os.name != "nt": return False
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetCurrentProcess()
        if mode == "low": k32.SetPriorityClass(h, 0x00000020)
        elif mode == "high": k32.SetPriorityClass(h, 0x00000080)
        else: k32.SetPriorityClass(h, 0x00008000)
        return True
    except Exception:
        return False


def toggle_window_visibility() -> None:
    global _main_hidden
    if _main_window is None: return
    try:
        if not _main_hidden:
            _main_window.hide(); _main_hidden = True
            if _tray_icon: _tray_icon.visible = True
        else:
            _main_window.show(); _main_hidden = False
            if _tray_icon: _tray_icon.visible = False
    except Exception:
        pass


def start_global_hotkey(key_name: str) -> bool:
    global _hk_thread
    stop_global_hotkey()
    if os.name != "nt" or not key_name: return False
    vk = VK_MAP.get(key_name)
    if vk is None and len(key_name) == 1 and key_name.isalnum(): vk = ord(key_name.upper())
    if vk is None: return False

    def _loop():
        try:
            u32 = ctypes.windll.user32
            if not u32.RegisterHotKey(None, _HK_ID, MOD_NOREPEAT, vk): return
            msg = ctypes.wintypes.MSG()
            try:
                while not _hk_stop.is_set():
                    r = u32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                    if r in (0, -1): break
                    if msg.message == WM_HOTKEY and msg.wParam == _HK_ID:
                        toggle_window_visibility()
                    u32.TranslateMessage(ctypes.byref(msg)); u32.DispatchMessageW(ctypes.byref(msg))
            finally:
                u32.UnregisterHotKey(None, _HK_ID)
        except Exception:
            pass

    _hk_stop.clear()
    _hk_thread = threading.Thread(target=_loop, daemon=True); _hk_thread.start()
    return True


def stop_global_hotkey() -> None:
    global _hk_thread
    if _hk_thread and _hk_thread.is_alive():
        _hk_stop.set()
        if os.name == "nt":
            try: ctypes.windll.user32.PostThreadMessageW(_hk_thread.ident, WM_QUIT, 0, 0)
            except Exception: pass
        _hk_thread.join(timeout=1.0)
    _hk_thread = None; _hk_stop.clear()


def init_system_tray() -> None:
    global _tray_icon
    if not (HAS_PYSTRAY and HAS_PIL) or _tray_icon is not None: return
    try:
        img = Image.new("RGB", (64, 64), color="#f4ede1"); draw = ImageDraw.Draw(img)
        draw.ellipse([24,40,40,54], fill="#1e3a5f"); draw.ellipse([14,26,24,38], fill="#1e3a5f")
        draw.ellipse([24,22,34,34], fill="#1e3a5f"); draw.ellipse([34,22,44,34], fill="#1e3a5f")
        draw.ellipse([44,26,54,38], fill="#1e3a5f")
        def on_show(icon, item):
            global _main_hidden
            if _main_window: _main_window.show()
            _main_hidden = False
        def on_exit(icon, item):
            try: icon.stop()
            except Exception: pass
            stop_global_hotkey()
            if _main_window:
                try: _main_window.destroy()
                except Exception: pass
        menu = pystray.Menu(pystray.MenuItem("Restore Kitty", on_show, default=True),
                            pystray.MenuItem("Exit", on_exit))
        _tray_icon = pystray.Icon("kitty_ide", img, APP_NAME, menu)
        threading.Thread(target=_tray_icon.run, daemon=True).start()
    except Exception:
        _tray_icon = None


# ═══════════════════════════════════════════════════════════════════════════════
#  ROBLOX VERSION DISCOVERY + LAUNCHER (including suspended launch)
# ═══════════════════════════════════════════════════════════════════════════════

def list_installed_versions() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    lad = os.environ.get("LOCALAPPDATA")
    if not lad:
        return out
    root = Path(lad) / "Roblox" / "Versions"
    if not root.is_dir():
        return out
    try:
        for d in sorted(root.iterdir()):
            if not d.is_dir(): continue
            exe = d / "RobloxPlayerBeta.exe"
            if not exe.is_file(): continue
            try: mtime = exe.stat().st_mtime
            except Exception: mtime = 0
            out.append({"name": d.name, "path": str(d), "exe": str(exe), "modified": mtime})
    except Exception:
        pass
    out.sort(key=lambda r: -r["modified"])
    return out


def _launch_suspended(exe_path: str) -> Dict[str, Any]:
    """Launch RobloxPlayerBeta.exe with CREATE_SUSPENDED so we can inject
    before the client's own version check / integrity scanner runs."""
    try:
        k32 = ctypes.windll.kernel32
        startup = ctypes.STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        pi = ctypes.PROCESS_INFORMATION()
        cmd = f'"{exe_path}"'
        ok = k32.CreateProcessW(
            None, ctypes.c_wchar_p(cmd), None, None, False,
            CREATE_SUSPENDED, None, ctypes.c_wchar_p(str(Path(exe_path).parent)),
            ctypes.byref(startup), ctypes.byref(pi))
        if not ok:
            err = ctypes.GetLastError()
            return {"ok": False, "error": f"CreateProcessW failed (error {err})"}
        return {
            "ok": True,
            "pid": int(pi.dwProcessId),
            "process_handle": int(pi.hProcess),
            "thread_handle": int(pi.hThread),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _resume_process(thread_handle: int) -> bool:
    try:
        k32 = ctypes.windll.kernel32
        return k32.ResumeThread(ctypes.wintypes.HANDLE(thread_handle)) != 0xFFFFFFFF
    except Exception:
        return False


def _close_handle(h: int) -> None:
    try:
        ctypes.windll.kernel32.CloseHandle(ctypes.wintypes.HANDLE(h))
    except Exception:
        pass


def _launch_normal(exe_path: str) -> Dict[str, Any]:
    try:
        p = subprocess.Popen([exe_path], close_fds=True)
        return {"ok": True, "pid": p.pid}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
#  CORE INJECTION PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

def _prepare_kernel32():
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = ctypes.wintypes.HANDLE
    k32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    k32.VirtualAllocEx.restype = ctypes.c_void_p
    k32.VirtualAllocEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
    k32.WriteProcessMemory.restype = ctypes.wintypes.BOOL
    k32.WriteProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.ReadProcessMemory.restype = ctypes.wintypes.BOOL
    k32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                      ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.GetModuleHandleW.restype = ctypes.wintypes.HMODULE
    k32.GetModuleHandleW.argtypes = [ctypes.wintypes.LPCWSTR]
    k32.GetProcAddress.restype = ctypes.c_void_p
    k32.GetProcAddress.argtypes = [ctypes.wintypes.HMODULE, ctypes.wintypes.LPCSTR]
    k32.CreateRemoteThread.restype = ctypes.wintypes.HANDLE
    k32.CreateRemoteThread.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t,
                                       ctypes.c_void_p, ctypes.c_void_p, ctypes.wintypes.DWORD,
                                       ctypes.POINTER(ctypes.wintypes.DWORD)]
    k32.WaitForSingleObject.restype = ctypes.wintypes.DWORD
    k32.WaitForSingleObject.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD]
    k32.VirtualFreeEx.restype = ctypes.wintypes.BOOL
    k32.VirtualFreeEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD]
    k32.CloseHandle.restype = ctypes.wintypes.BOOL
    k32.CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    k32.GetLastError.restype = ctypes.wintypes.DWORD
    k32.GetLastError.argtypes = []
    return k32


def _write_process_memory(k32, h, addr: int, data: bytes) -> bool:
    try:
        buf = ctypes.create_string_buffer(data, len(data))
        written = ctypes.c_size_t(0)
        ok = k32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, len(data), ctypes.byref(written))
        return bool(ok) and written.value == len(data)
    except Exception:
        return False


def _read_process_memory(k32, h, addr: int, size: int) -> Optional[bytes]:
    try:
        buf = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t(0)
        if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(read)):
            return buf.raw[:read.value]
    except Exception:
        pass
    return None


def inject_loadlibrary(pid: int, dll_path: str) -> Dict[str, Any]:
    """Standard CreateRemoteThread + LoadLibraryA injection.

    Works on the running client. Used as the fallback path and for the
    normal-latest case.
    """
    k32 = _prepare_kernel32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        err = k32.GetLastError()
        return {"ok": False, "error": f"OpenProcess failed for PID {pid} (error {err} — run as admin)"}
    try:
        path_bytes = dll_path.encode("mbcs") + b"\x00"
        addr = k32.VirtualAllocEx(h, None, len(path_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr:
            err = k32.GetLastError()
            return {"ok": False, "error": f"VirtualAllocEx failed (error {err})"}
        if not _write_process_memory(k32, h, addr, path_bytes):
            return {"ok": False, "error": "WriteProcessMemory failed"}
        k32.GetModuleHandleW.restype = ctypes.wintypes.HMODULE
        k32.GetModuleHandleW.argtypes = [ctypes.wintypes.LPCWSTR]
        kernel32_mod = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kernel32_mod, b"LoadLibraryA")
        if not ll:
            return {"ok": False, "error": "GetProcAddress(LoadLibraryA) failed"}
        tid = ctypes.wintypes.DWORD()
        th = k32.CreateRemoteThread(h, None, 0, ll, addr, 0, ctypes.byref(tid))
        if not th:
            err = k32.GetLastError()
            return {"ok": False, "error": f"CreateRemoteThread failed (error {err})"}
        k32.WaitForSingleObject(th, 15000)
        k32.CloseHandle(th)
        k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
        return {"ok": True, "pid": pid, "method": "loadlibrary"}
    finally:
        k32.CloseHandle(h)


def inject_ntcreatethread(pid: int, dll_path: str) -> Dict[str, Any]:
    """Inject via NtCreateThreadEx using LoadLibraryW. Slightly stealthier
    than CreateRemoteThread (some AVs hook CRT but not NTCT)."""
    try:
        ntdll = ctypes.WinDLL("ntdll")
    except Exception as e:
        return {"ok": False, "error": f"ntdll load failed: {e}"}
    k32 = _prepare_kernel32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        err = k32.GetLastError()
        return {"ok": False, "error": f"OpenProcess failed for PID {pid} (error {err})"}
    try:
        path_bytes = dll_path.encode("utf-16-le") + b"\x00\x00"
        addr = k32.VirtualAllocEx(h, None, len(path_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr:
            return {"ok": False, "error": "VirtualAllocEx failed"}
        if not _write_process_memory(k32, h, addr, path_bytes):
            return {"ok": False, "error": "WriteProcessMemory failed"}
        kernel32_mod = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kernel32_mod, b"LoadLibraryW")
        if not ll:
            return {"ok": False, "error": "GetProcAddress(LoadLibraryW) failed"}

        class _OBJECT_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Length", ctypes.wintypes.ULONG),
                        ("RootDirectory", ctypes.wintypes.HANDLE),
                        ("ObjectName", ctypes.c_void_p),
                        ("Attributes", ctypes.wintypes.ULONG),
                        ("SecurityDescriptor", ctypes.c_void_p),
                        ("SecurityQualityOfService", ctypes.c_void_p)]
        class _CLIENT_ID(ctypes.Structure):
            _fields_ = [("UniqueProcess", ctypes.c_void_p), ("UniqueThread", ctypes.c_void_p)]

        NtCreateThreadEx = ntdll.NtCreateThreadEx
        NtCreateThreadEx.restype = ctypes.c_long
        NtCreateThreadEx.argtypes = [
            ctypes.POINTER(ctypes.wintypes.HANDLE),
            ctypes.wintypes.DWORD, ctypes.c_void_p, ctypes.wintypes.HANDLE,
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.wintypes.DWORD, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p,
        ]
        th = ctypes.wintypes.HANDLE()
        status = NtCreateThreadEx(ctypes.byref(th), 0x1FFFFF, None, h,
                                  ctypes.c_void_p(ll), ctypes.c_void_p(addr),
                                  0, 0, 0, 0, None)
        if status != 0 or not th:
            return {"ok": False, "error": f"NtCreateThreadEx failed (status 0x{status & 0xFFFFFFFF:X})"}
        k32.WaitForSingleObject(th, 15000)
        k32.CloseHandle(th)
        k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
        return {"ok": True, "pid": pid, "method": "ntcreatethread"}
    finally:
        k32.CloseHandle(h)


def patch_client_version_string(pid: int, latest_version: str) -> Dict[str, Any]:
    """Scan the client's memory for its version string and rewrite it to the
    'latest' string. This is what most legacy injectors do to convince the
    client its own version check passes when it is actually old.

    This is a best-effort approach. If Module.dll ships its own signature-based
    version-check hook (which most modern modules do), leave this off.
    """
    if not latest_version or not latest_version.startswith("version-"):
        return {"ok": False, "error": "latest version string not provided"}

    k32 = _prepare_kernel32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        return {"ok": False, "error": "OpenProcess for memory scan failed"}
    try:
        versions = list_installed_versions()
        if not versions:
            return {"ok": False, "error": "no installed versions to derive strings from"}
        own_version = next((v["name"] for v in versions if v["name"] != latest_version), None)
        if not own_version:
            return {"ok": False, "error": "no old version string available"}

        needle = own_version.encode("ascii")
        repl = latest_version.encode("ascii")
        if len(needle) != len(repl):
            return {"ok": False, "error": "version strings differ in length"}

        # Walk committed regions of the process and look for the string
        class _MBI(ctypes.Structure):
            _fields_ = [
                ("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.wintypes.DWORD),
                ("RegionSize", ctypes.c_size_t), ("State", ctypes.wintypes.DWORD),
                ("Protect", ctypes.wintypes.DWORD), ("Type", ctypes.wintypes.DWORD),
            ]
        VirtualQueryEx = k32.VirtualQueryEx
        VirtualQueryEx.restype = ctypes.c_size_t
        VirtualQueryEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p,
                                   ctypes.POINTER(_MBI), ctypes.c_size_t]

        addr = 0
        hits = 0
        scanned = 0
        while scanned < (2 << 30):  # cap at 2GB scanned
            mbi = _MBI()
            res = VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
            if not res:
                break
            base = int(mbi.BaseAddress or 0)
            size = int(mbi.RegionSize or 0)
            if size == 0:
                break
            if (mbi.State == 0x1000 and
                mbi.Protect in (0x02, 0x04, 0x20, 0x40, 0x80) and
                base > 0 and size < (128 << 20)):
                CHUNK = 1 << 20
                off = 0
                while off < size:
                    to_read = min(CHUNK, size - off)
                    buf = _read_process_memory(k32, h, base + off, to_read)
                    if buf:
                        i = 0
                        while True:
                            i = buf.find(needle, i)
                            if i == -1: break
                            hit_addr = base + off + i
                            if _write_process_memory(k32, h, hit_addr, repl):
                                hits += 1
                            i += len(needle)
                    off += to_read
            scanned += size
            addr = base + size
            if addr <= 0:
                break

        return {"ok": hits > 0, "hits": hits,
                "note": f"Patched {hits} instance(s) of {own_version} → {latest_version}" if hits else "no matches found (already latest or memory protected)"}
    finally:
        k32.CloseHandle(h)


def inject_early_bird(pid: int, dll_path: str) -> Dict[str, Any]:
    """Early-bird: process is suspended via CreateProcess, we inject before
    the client's own integrity / version checks run, then we resume it."""
    k32 = _prepare_kernel32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        return {"ok": False, "error": "OpenProcess for early-bird failed"}
    try:
        path_bytes = dll_path.encode("mbcs") + b"\x00"
        addr = k32.VirtualAllocEx(h, None, len(path_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr:
            return {"ok": False, "error": "VirtualAllocEx failed"}
        if not _write_process_memory(k32, h, addr, path_bytes):
            return {"ok": False, "error": "WriteProcessMemory failed"}
        kernel32_mod = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kernel32_mod, b"LoadLibraryA")
        if not ll:
            return {"ok": False, "error": "GetProcAddress failed"}
        tid = ctypes.wintypes.DWORD()
        th = k32.CreateRemoteThread(h, None, 0, ll, addr, 0, ctypes.byref(tid))
        if not th:
            return {"ok": False, "error": "CreateRemoteThread failed"}
        k32.WaitForSingleObject(th, 15000)
        k32.CloseHandle(th)
        # Deliberately do NOT free the path buffer here; some modules read
        # the path during DllMain. Free it after a short delay instead.
        def _free_later():
            time.sleep(3.0)
            try: k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
            except Exception: pass
        threading.Thread(target=_free_later, daemon=True).start()
        return {"ok": True, "pid": pid, "method": "early-bird"}
    finally:
        # Don't close h immediately; injection succeeded and the buffer free
        # thread still needs it. Leak for a few seconds, then close.
        def _close_later():
            time.sleep(3.5)
            try: k32.CloseHandle(h)
            except Exception: pass
        threading.Thread(target=_close_later, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
#  BACKEND CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════

class KittyBackend:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.runtime_mode = "pywebview" if HAS_PYWEBVIEW else "browser"
        self.is_maximized = False
        self.attached = False
        self._attached_pid: Optional[int] = None
        self._attached_version = ""
        self._attached_method = ""
        self.settings = self._load_settings()
        self.scripts = self._load_scripts()
        self._last_sync: Dict[str, Any] = {}
        threading.Thread(target=self._offset_watcher, daemon=True).start()

    # ── Offsets ────────────────────────────────────────────────────────────
    def _offsets_paths(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return {
            "dir": CACHE_DIR,
            "offsets": CACHE_DIR / "offsets.json",
            "version": CACHE_DIR / "offsets_version.txt",
            "meta": CACHE_DIR / "offsets_meta.json",
        }

    def _fetch_url(self, url: str, timeout: int = 25) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}-Offsets/{APP_VERSION}"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()

    def sync_offsets(self, force: bool = False) -> Dict[str, Any]:
        with self._lock:
            p = self._offsets_paths()
            cached_version = ""
            if p["version"].is_file():
                try: cached_version = p["version"].read_text(encoding="utf-8").strip()
                except Exception: cached_version = ""

            live_version = cached_version
            try:
                live_version = self._fetch_url("https://offsets.imtheo.lol/roblox/version", timeout=10).decode("utf-8", "ignore").strip()
            except Exception as exc:
                if p["offsets"].is_file():
                    res = {"ok": True, "cached": True, "version": cached_version,
                           "note": f"version probe failed ({exc}); using cache"}
                    self._last_sync = res
                    return res
                res = {"ok": False, "error": f"version probe failed: {exc}", "cached_version": cached_version}
                self._last_sync = res
                return res

            needs_fetch = force or not p["offsets"].is_file() or (live_version and live_version != cached_version)
            if not needs_fetch:
                res = {"ok": True, "cached": True, "version": cached_version}
                self._last_sync = res
                return res

            try:
                raw = self._fetch_url("https://offsets.imtheo.lol/offsets.json", timeout=30)
                if not raw or len(raw) < 64:
                    res = {"ok": False, "error": "offsets payload too small", "cached_version": cached_version}
                    self._last_sync = res
                    return res
                p["offsets"].write_bytes(raw)
                if live_version:
                    p["version"].write_text(live_version, encoding="utf-8")
                atomic_write_json(p["meta"], {
                    "version": live_version or cached_version or "unknown",
                    "fetched": datetime.now().isoformat(),
                    "bytes": len(raw),
                    "source": "offsets.imtheo.lol",
                })
                res = {"ok": True, "fetched": True, "version": live_version or cached_version,
                       "bytes": len(raw), "changed": live_version != cached_version}
                self._last_sync = res
                return res
            except Exception as exc:
                res = {"ok": False, "error": f"offsets fetch failed: {exc}", "cached_version": cached_version}
                self._last_sync = res
                return res

    def offsets_status(self) -> Dict[str, Any]:
        p = self._offsets_paths()
        cached_version = ""
        meta = {}
        if p["version"].is_file():
            try: cached_version = p["version"].read_text(encoding="utf-8").strip()
            except Exception: cached_version = ""
        if p["meta"].is_file():
            try: meta = json.loads(p["meta"].read_text(encoding="utf-8"))
            except Exception: meta = {}
        dll = _resolve_dll()
        return {
            "ok": True,
            "cached_version": cached_version,
            "offsets_cached": p["offsets"].is_file(),
            "offsets_bytes": p["offsets"].stat().st_size if p["offsets"].is_file() else 0,
            "last_sync": meta.get("fetched", ""),
            "source": "offsets.imtheo.lol",
            "module_dir": str(_module_dir()),
            "runtime_dir": str(APP_RUNTIME_DIR),
            "dll_path": str(dll) if dll else "",
            "dll_found": bool(dll),
        }

    def _offset_watcher(self):
        time.sleep(2.0)
        while True:
            try:
                self.sync_offsets()
            except Exception:
                pass
            time.sleep(30 * 60)

    # ── Module config ─────────────────────────────────────────────────────
    def _write_module_config(self, pid: Optional[int] = None, target_version: str = ""):
        module_dir = _module_dir()
        try:
            module_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            return

        s = self.settings
        rb = s.get("roblox", {})
        gen = s.get("general", {})
        p = self._offsets_paths()

        config = {
            "schema": 3,
            "app": APP_NAME,
            "appVersion": APP_VERSION,
            "writtenAt": datetime.now().isoformat(),
            "targetPid": pid,
            "clientVersion": target_version or (self._attached_version if pid == self._attached_pid else ""),

            # Executor feature switches
            "raknet":           bool(rb.get("raknet", False)),
            "internalUI":       bool(rb.get("internalUI", False)),
            "bypassAFK":        bool(rb.get("bypassAFK", True)),
            "skipVersionCheck": bool(rb.get("skipVersionCheck", True)),
            "forceOldVersionBypass": bool(rb.get("forceOldVersionBypass", True)),
            "autoExec":         bool(rb.get("autoAttach", False)),
            "autoInject":       bool(rb.get("autoInject", False)),
            "injectTimeoutSec": int(rb.get("injectTimeoutSec", 60)),

            # Storage paths
            "offsetsFile":      str(p["offsets"]),
            "offsetsVersion":   (p["version"].read_text(encoding="utf-8").strip()
                                 if p["version"].is_file() else ""),
            "autoexecDir":      str(AUTOEXEC_DIR),
            "scriptsDir":       str(SCRIPTS_DIR),
            "cacheDir":         str(CACHE_DIR),
            "dataDir":          str(APP_DIR),
            "moduleDir":        str(module_dir),

            # Exec socket
            "execHost":         str(rb.get("execHost", EXEC_HOST)),
            "execPort":         int(rb.get("execPort", EXEC_PORT)),

            # Identity
            "userName":         str(gen.get("userName", "")),
            "planName":         str(gen.get("planName", "")),
        }

        atomic_write_json(module_dir / "kitty_module_config.json", config)
        try:
            env_lines = [
                f"KITTY_RAKNET={'1' if config['raknet'] else '0'}",
                f"KITTY_INTERNAL_UI={'1' if config['internalUI'] else '0'}",
                f"KITTY_BYPASS_AFK={'1' if config['bypassAFK'] else '0'}",
                f"KITTY_SKIP_VERSION={'1' if config['skipVersionCheck'] else '0'}",
                f"KITTY_FORCE_OLD_BYPASS={'1' if config['forceOldVersionBypass'] else '0'}",
                f"KITTY_AUTOEXEC={'1' if config['autoExec'] else '0'}",
                f"KITTY_OFFSETS_FILE={config['offsetsFile']}",
                f"KITTY_AUTOEXEC_DIR={config['autoexecDir']}",
                f"KITTY_EXEC_HOST={config['execHost']}",
                f"KITTY_EXEC_PORT={config['execPort']}",
                f"KITTY_CLIENT_VERSION={config['clientVersion']}",
                f"KITTY_TARGET_PID={config['targetPid']}",
            ]
            (module_dir / "kitty_module.env").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    def _pre_inject(self, pid: Optional[int], target_version: str = ""):
        try: self.sync_offsets()
        except Exception: pass
        try: self._write_module_config(pid, target_version)
        except Exception: pass

    # ── Settings / scripts ────────────────────────────────────────────────
    def _deep_merge(self, default, loaded):
        out = {}
        for k, dv in default.items():
            if k not in loaded: out[k] = json.loads(json.dumps(dv)); continue
            lv = loaded[k]
            if isinstance(dv, dict) and isinstance(lv, dict): out[k] = self._deep_merge(dv, lv)
            elif isinstance(dv, bool): out[k] = bool(lv)
            elif isinstance(dv, int) and not isinstance(dv, bool):
                try: out[k] = int(lv)
                except Exception: out[k] = dv
            elif isinstance(dv, float):
                try: out[k] = float(lv)
                except Exception: out[k] = dv
            elif isinstance(dv, str): out[k] = str(lv) if lv is not None else dv
            elif isinstance(dv, list): out[k] = lv if isinstance(lv, list) else list(dv)
            else: out[k] = lv
        return out

    def _load_settings(self):
        with self._lock:
            defaults = get_flat_defaults()
            if not SETTINGS_FILE.is_file():
                atomic_write_json(SETTINGS_FILE, defaults); return defaults
            try:
                raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                if not isinstance(raw, dict): raise ValueError("root")
                merged = self._deep_merge(defaults, raw)
            except Exception:
                merged = defaults; atomic_write_json(SETTINGS_FILE, merged)
            ct = merged.get("appearance", {}).get("customTheme", {})
            img_name = ct.get("imageFilename", "")
            if img_name:
                img_path = THEMES_DIR / Path(img_name).name
                if img_path.is_file():
                    try:
                        mime = mimetypes.guess_type(img_path.name)[0] or "image/png"
                        b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
                        ct["imageDataUrl"] = f"data:{mime};base64,{b64}"
                    except Exception: ct["imageDataUrl"] = ""
                else:
                    ct["imageFilename"] = ""; ct["imageDataUrl"] = ""
            return merged

    def _save_settings_to_disk(self):
        with self._lock:
            copy = json.loads(json.dumps(self.settings))
            ct = copy.get("appearance", {}).get("customTheme", {})
            if ct.get("imageFilename"): ct["imageDataUrl"] = ""
            return atomic_write_json(SETTINGS_FILE, copy)

    def _load_scripts(self):
        items = [dict(x) for x in DEFAULT_SCRIPTS]
        for folder_name, folder_path in (("Scripts", SCRIPTS_DIR), ("AutoExec", AUTOEXEC_DIR)):
            try:
                for p in sorted(folder_path.glob("*")):
                    disabled = folder_name == "AutoExec" and p.name.lower().endswith((".lua.disabled", ".luau.disabled", ".txt.disabled"))
                    if p.is_file() and (p.suffix.lower() in ALLOWED_SCRIPT_EXTS or disabled):
                        try:
                            items.append({
                                "id": f"disk_{folder_name}_{p.stem}_{abs(hash(p.name)) % 9999}",
                                "title": p.name, "folder": folder_name,
                                "content": p.read_text(encoding="utf-8", errors="replace"),
                                "disabled": disabled})
                        except Exception: pass
            except Exception: pass
        return items

    # ── Public API ────────────────────────────────────────────────────────
    def get_initial_state(self):
        with self._lock:
            recovery = None
            if RECOVERY_FILE.is_file():
                try: recovery = json.loads(RECOVERY_FILE.read_text(encoding="utf-8"))
                except Exception: recovery = None
            return {
                "ok": True,
                "app": {"name": APP_NAME, "version": APP_VERSION, "build": APP_BUILD,
                        "runtimeMode": self.runtime_mode,
                        "platform": f"{platform.system()} {platform.release()}",
                        "pythonVersion": platform.python_version(),
                        "settingsPath": str(SETTINGS_FILE),
                        "themesDir": str(THEMES_DIR),
                        "scriptsDir": str(SCRIPTS_DIR),
                        "runtimeDir": str(APP_RUNTIME_DIR),
                        "hasPil": HAS_PIL, "hasPystray": HAS_PYSTRAY, "hasPsutil": HAS_PSUTIL},
                "settings": self.settings,
                "sectionDefaults": SECTION_DEFAULTS,
                "builtinThemes": BUILTIN_THEMES,
                "scripts": self.scripts,
                "recovery": recovery,
                "attached": self.attached,
                "profilePicture": self._get_profile_picture(),
                "offsets": self.offsets_status(),
                "installedVersions": list_installed_versions(),
            }

    def update_settings(self, payload):
        with self._lock:
            if not isinstance(payload, dict): return {"ok": False, "error": "Invalid"}
            self.settings = self._deep_merge(self.settings, payload)
            saved = self._save_settings_to_disk()
            gen = self.settings.get("general", {})
            apply_streamproof_win32(bool(gen.get("streamproof", False)))
            apply_process_priority_win32(str(gen.get("performanceMode", "medium")))
            if _main_window is not None:
                try: _main_window.set_title("Spotify" if gen.get("disguiseMode") else APP_NAME)
                except Exception: pass
            # Keep the module config fresh so a re-inject doesn't need UI interaction
            try: self._write_module_config(self._attached_pid)
            except Exception: pass
            return {"ok": saved, "settings": self.settings}

    def reset_all_settings(self):
        with self._lock:
            self.settings = get_flat_defaults(); self._save_settings_to_disk()
            return {"ok": True, "settings": self.settings}

    def _get_profile_picture(self):
        if not AVATAR_FILE.is_file(): return None
        try:
            mime = mimetypes.guess_type(AVATAR_FILE.name)[0] or "image/png"
            b64 = base64.b64encode(AVATAR_FILE.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{b64}"
        except Exception: return None

    def pick_theme_image(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            res = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False,
                file_types=("Image Files (*.png;*.jpg;*.jpeg;*.webp)", "All files (*.*)"))
            if not res: return {"ok": False, "cancelled": True}
            path = Path(res[0] if isinstance(res, (list, tuple)) else res)
            if path.suffix.lower() not in ALLOWED_IMAGE_EXTS:
                return {"ok": False, "error": "Unsupported image type."}
            raw = path.read_bytes()
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            return {"ok": True, "filename": path.name,
                    "dataUrl": f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def pick_profile_image(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            res = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False,
                file_types=("Image Files (*.png;*.jpg;*.jpeg;*.webp)", "All files (*.*)"))
            if not res: return {"ok": False, "cancelled": True}
            path = Path(res[0] if isinstance(res, (list, tuple)) else res)
            raw = path.read_bytes()
            PROFILE_DIR.mkdir(parents=True, exist_ok=True)
            AVATAR_FILE.write_bytes(raw)
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            return {"ok": True, "dataUrl": f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def save_profile_image(self, payload):
        try:
            data_url = str(payload.get("dataUrl") or "")
            if not data_url.startswith("data:image/"): return {"ok": False, "error": "Invalid image"}
            _, b64 = data_url.split(",", 1)
            raw = base64.b64decode(b64)
            if len(raw) < 32: return {"ok": False, "error": "Image corrupted"}
            PROFILE_DIR.mkdir(parents=True, exist_ok=True)
            AVATAR_FILE.write_bytes(raw)
            return {"ok": True}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def remove_profile_image(self):
        try:
            if AVATAR_FILE.is_file(): AVATAR_FILE.unlink()
            return {"ok": True}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def save_custom_theme_image(self, payload):
        with self._lock:
            try:
                filename = str(payload.get("filename") or "wallpaper.png")
                data_url = str(payload.get("dataUrl") or "")
                palette = payload.get("palette")
                if not data_url.startswith("data:image/"): return {"ok": False, "error": "Invalid image data URL"}
                header, b64 = data_url.split(",", 1)
                raw = base64.b64decode(b64)
                if len(raw) < 32: return {"ok": False, "error": "Image corrupted"}
                ext = Path(filename).suffix.lower()
                if ext not in ALLOWED_IMAGE_EXTS:
                    ext = ".webp" if "webp" in header else (".jpg" if "jpeg" in header else ".png")
                safe_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", Path(filename).stem)[:32]
                stored_name = f"theme_{safe_stem}_{int(time.time())}{ext}"
                target = THEMES_DIR / stored_name
                target.write_bytes(raw)
                ct = self.settings["appearance"]["customTheme"]
                ct["name"] = Path(filename).stem[:28] or "Custom Image"
                ct["imageFilename"] = stored_name
                ct["imageDataUrl"] = data_url
                if isinstance(palette, dict): ct["palette"] = palette
                self._save_settings_to_disk()
                return {"ok": True, "customTheme": ct, "settings": self.settings}
            except Exception as exc: return {"ok": False, "error": str(exc)}

    def remove_custom_theme_image(self):
        with self._lock:
            ct = self.settings["appearance"]["customTheme"]
            old_name = ct.get("imageFilename", "")
            if old_name:
                p = THEMES_DIR / Path(old_name).name
                if p.is_file():
                    try: p.unlink()
                    except Exception: pass
            ct["imageFilename"] = ""; ct["imageDataUrl"] = ""
            ct["palette"] = dict(BUILTIN_THEMES["kitty"])
            self.settings["appearance"]["useBackgroundImage"] = False
            self._save_settings_to_disk()
            return {"ok": True, "settings": self.settings}

    def clear_theme_cache(self):
        with self._lock:
            removed = 0
            active = self.settings["appearance"]["customTheme"].get("imageFilename", "")
            for p in THEMES_DIR.glob("*"):
                if p.is_file() and p.name != active:
                    try: p.unlink(); removed += 1
                    except Exception: pass
            return {"ok": True, "removed": removed}

    def open_script_file(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            res = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False,
                file_types=("Luau & Lua Scripts (*.luau;*.lua;*.txt)", "All files (*.*)"))
            if not res: return {"ok": False, "cancelled": True}
            p = Path(res[0] if isinstance(res, (list, tuple)) else res)
            return {"ok": True, "filename": p.name,
                    "content": p.read_text(encoding="utf-8", errors="replace"), "path": str(p)}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def save_script_file(self, payload):
        raw_name = str(payload.get("filename") or "Untitled.luau")
        to_autoexec = raw_name.replace("\\", "/").lower().startswith("autoexec/")
        direct = bool(payload.get("direct", False))
        filename = Path(raw_name).name
        if not Path(filename).suffix: filename += ".luau"
        content = str(payload.get("content") or "")
        if to_autoexec:
            try:
                AUTOEXEC_DIR.mkdir(parents=True, exist_ok=True)
                target = AUTOEXEC_DIR / filename
                target.write_text(content, encoding="utf-8")
                return {"ok": True, "filename": filename, "path": str(target), "folder": "AutoExec"}
            except Exception as exc: return {"ok": False, "error": str(exc)}
        if direct:
            try:
                SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
                target = SCRIPTS_DIR / filename
                target.write_text(content, encoding="utf-8")
                return {"ok": True, "filename": filename, "path": str(target), "direct": True}
            except Exception as exc: return {"ok": False, "error": str(exc)}
        if HAS_PYWEBVIEW and _main_window is not None:
            try:
                res = _main_window.create_file_dialog(webview.SAVE_DIALOG, save_filename=filename,
                    file_types=("Luau Script (*.luau)", "Lua Script (*.lua)", "Text File (*.txt)"))
                if not res: return {"ok": False, "cancelled": True}
                p = Path(res if isinstance(res, str) else res[0])
                p.write_text(content, encoding="utf-8")
                return {"ok": True, "filename": p.name, "path": str(p)}
            except Exception as exc: return {"ok": False, "error": str(exc)}
        target = SCRIPTS_DIR / filename
        target.write_text(content, encoding="utf-8")
        return {"ok": True, "filename": filename, "path": str(target), "browserDownload": True}

    def manage_script_file(self, payload):
        try:
            folder = str(payload.get("folder") or "")
            action = str(payload.get("action") or "")
            filename = Path(str(payload.get("filename") or "")).name
            if not filename or filename in {".", ".."} or Path(filename).name != filename:
                return {"ok": False, "error": "Invalid filename."}
            base = SCRIPTS_DIR if folder == "Scripts" else (AUTOEXEC_DIR if folder == "AutoExec" else None)
            if base is None: return {"ok": False, "error": "Unsupported folder."}
            base.mkdir(parents=True, exist_ok=True)
            target = base / filename
            if not target.is_file(): return {"ok": False, "error": "File not found."}
            if action == "delete":
                target.unlink(); return {"ok": True, "filename": filename}
            if folder == "AutoExec" and action == "disable":
                if filename.lower().endswith(".disabled"): return {"ok": False, "error": "Already disabled."}
                dest = target.with_name(target.name + ".disabled")
                if dest.exists(): return {"ok": False, "error": "Disabled copy exists."}
                target.rename(dest); return {"ok": True, "filename": dest.name, "disabled": True}
            if folder == "Scripts" and action == "rename":
                new_name = Path(str(payload.get("newFilename") or "")).name
                if not new_name or Path(new_name).suffix.lower() not in ALLOWED_SCRIPT_EXTS:
                    return {"ok": False, "error": "Use a .lua, .luau, or .txt extension."}
                dest = base / new_name
                if dest.exists() and dest != target:
                    return {"ok": False, "error": "Name already in use."}
                target.rename(dest); return {"ok": True, "filename": dest.name}
            return {"ok": False, "error": "Unsupported action."}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def export_settings_json(self):
        with self._lock:
            copy = json.loads(json.dumps(self.settings))
            copy.get("appearance", {}).get("customTheme", {})["imageDataUrl"] = ""
            raw_json = json.dumps(copy, indent=2)
            if HAS_PYWEBVIEW and _main_window is not None:
                try:
                    res = _main_window.create_file_dialog(webview.SAVE_DIALOG, save_filename="kitty_settings.json",
                        file_types=("JSON Files (*.json)", "All files (*.*)"))
                    if not res: return {"ok": False, "cancelled": True}
                    p = Path(res if isinstance(res, str) else res[0])
                    p.write_text(raw_json, encoding="utf-8")
                    return {"ok": True, "path": str(p)}
                except Exception as exc: return {"ok": False, "error": str(exc)}
            return {"ok": True, "json": raw_json, "browserDownload": True}

    def import_settings_json(self, payload):
        with self._lock:
            raw_text = str(payload.get("json") or "")
            if not raw_text and HAS_PYWEBVIEW and _main_window is not None:
                try:
                    res = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False,
                        file_types=("JSON Files (*.json)", "All files (*.*)"))
                    if not res: return {"ok": False, "cancelled": True}
                    p = Path(res[0] if isinstance(res, (list, tuple)) else res)
                    raw_text = p.read_text(encoding="utf-8")
                except Exception as exc: return {"ok": False, "error": str(exc)}
            try:
                parsed = json.loads(raw_text)
                if not isinstance(parsed, dict): raise ValueError("root")
                self.settings = self._deep_merge(get_flat_defaults(), parsed)
                self._save_settings_to_disk()
                return {"ok": True, "settings": self.settings}
            except Exception as exc: return {"ok": False, "error": f"Invalid settings JSON: {exc}"}

    def open_data_folder(self):
        try:
            if os.name == "nt": os.startfile(str(APP_DIR))
            elif sys.platform == "darwin": os.system(f'open "{APP_DIR}"')
            else: os.system(f'xdg-open "{APP_DIR}"')
            return {"ok": True}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    # ── Roblox process helpers ────────────────────────────────────────────
    def _get_roblox_pids(self):
        if HAS_PSUTIL:
            pids = []
            for proc in psutil.process_iter(["pid", "name"]):
                try: name = (proc.info.get("name") or "").lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied): continue
                if "robloxplayerbeta" in name:
                    pids.append(proc.info["pid"])
            return pids
        if os.name == "nt":
            try:
                out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq RobloxPlayerBeta.exe", "/FO", "CSV", "/NH"],
                                     capture_output=True, text=True, timeout=8)
                pids = []
                for line in (out.stdout or "").splitlines():
                    if "robloxplayerbeta" in line.lower():
                        m = re.search(r"\",\"(\d+)\"", line)
                        if m: pids.append(int(m.group(1)))
                return pids
            except Exception:
                return []
        return []

    def kill_roblox(self):
        killed = 0
        for pid in self._get_roblox_pids():
            try:
                if HAS_PSUTIL:
                    psutil.Process(pid).kill()
                    killed += 1
                else:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                   capture_output=True, timeout=8)
                    killed += 1
            except Exception:
                pass
        self.attached = False; self._attached_pid = None
        return {"ok": True, "killed": killed}

    def get_status(self):
        try:
            conn = socket.create_connection((EXEC_HOST, EXEC_PORT), 1)
            conn.close(); attached = True
        except OSError:
            attached = False
        pids = self._get_roblox_pids()
        return {
            "attached": attached,
            "pids": pids,
            "roblox_running": bool(pids),
            "attached_pid": self._attached_pid,
            "attached_version": self._attached_version,
            "attached_method": self._attached_method,
        }

    # ── Injection orchestration ──────────────────────────────────────────
    def _do_inject(self, pid: int, method: str) -> Dict[str, Any]:
        dll = _resolve_dll()
        if not dll:
            return {"ok": False, "error": f"{DLL_NAME} not found. Put it in {APP_RUNTIME_DIR} or in ./bin/."}
        dll_str = str(dll)

        if method == "early-bird":
            res = inject_early_bird(pid, dll_str)
        elif method == "ntcreatethread":
            res = inject_ntcreatethread(pid, dll_str)
        else:
            res = inject_loadlibrary(pid, dll_str)

        if res.get("ok"):
            self.attached = True
            self._attached_pid = pid
            self._attached_version = _get_pid_version(pid) or ""
            self._attached_method = res.get("method", method)
        return res

    def simulate_attach(self, target_pid=None):
        with self._lock:
            pids = self._get_roblox_pids()
            if not pids:
                return {"ok": False, "error": "Roblox not running — use Launch & Inject instead."}
            pid = int(target_pid) if target_pid else pids[0]
            if pid not in pids: return {"ok": False, "error": f"PID {pid} not active"}

            self._pre_inject(pid, _get_pid_version(pid) or "")
            dll = _resolve_dll()
            if not dll: return {"ok": False, "error": f"{DLL_NAME} not found"}

            # Try methods in order of preference based on settings
            rb = self.settings.get("roblox", {})
            order = []
            if rb.get("useManualMapper", False):
                order = ["ntcreatethread", "loadlibrary"]
            else:
                order = ["loadlibrary", "ntcreatethread"]

            last_err = None
            for m in order:
                res = self._do_inject(pid, m)
                if res.get("ok"):
                    return {
                        "ok": True, "attached": True, "pid": pid,
                        "message": f"Injected {DLL_NAME} into PID {pid} ({res.get('method', m)})",
                        "clientVersion": self._attached_version,
                        "dll": str(dll),
                    }
                last_err = res.get("error")

            return {"ok": False, "error": last_err or "all injection methods failed"}

    def launch_and_inject(self, version: str = ""):
        """Launch a specific Roblox version and inject into it.

        Handles old-version bypass via:
          1. CREATE_SUSPENDED + early-bird injection (skips integrity/version scan)
          2. ClientVersion string patch (only if enabled and using latest target)
          3. Fall back to normal launch + attach
        """
        with self._lock:
            dll = _resolve_dll()
            if not dll:
                return {"ok": False, "error": f"{DLL_NAME} not found next to kitty.py"}

            # Already running? Offer to attach
            running = self._get_roblox_pids()
            if running:
                return {"ok": False, "error": f"Roblox already running (PID {running[0]}). Attach instead.",
                        "already_running": True, "pid": running[0]}

            installed = list_installed_versions()
            if not installed:
                return {"ok": False, "error": "No Roblox versions found in %LOCALAPPDATA%\\Roblox\\Versions"}

            # Pick target
            target = None
            if version:
                target = next((v for v in installed if v["name"] == version), None)
            if target is None:
                target = installed[0]  # newest by modified time

            rb = self.settings.get("roblox", {})
            prefer_suspended = rb.get("preferSuspendedInject", True)
            force_old = rb.get("forceOldVersionBypass", True)
            use_version_patch = rb.get("patchClientVersion", True)

            # Freshen offsets and write module config before touching the client
            self._pre_inject(None, target["name"])

            result: Dict[str, Any] = {"ok": False}

            if prefer_suspended:
                launch = _launch_suspended(target["exe"])
                if not launch.get("ok"):
                    # Fall through to normal launch
                    launch = None
                if launch:
                    pid = launch["pid"]
                    # Write config with the now-known PID
                    self._pre_inject(pid, target["name"])
                    # Early-bird inject while suspended
                    inj = self._do_inject(pid, "early-bird")
                    # Resume regardless — we don't want to leave it frozen
                    _resume_process(launch["thread_handle"])
                    time.sleep(1.0)
                    _close_handle(launch["process_handle"])
                    _close_handle(launch["thread_handle"])
                    if inj.get("ok"):
                        result = {
                            "ok": True, "attached": True, "pid": pid,
                            "message": f"Launched suspended + injected {DLL_NAME} into {target['name']}",
                            "method": "early-bird", "version": target["name"],
                            "dll": str(dll),
                        }
                    else:
                        # Early-bird failed; try normal inject after the process settles
                        time.sleep(2.0)
                        if _get_pid_version(pid):
                            retry = self._do_inject(pid, "loadlibrary")
                            if retry.get("ok"):
                                result = {
                                    "ok": True, "attached": True, "pid": pid,
                                    "message": f"Injected into {target['name']} (fallback)",
                                    "method": "loadlibrary", "version": target["name"],
                                    "dll": str(dll),
                                }
                            else:
                                result = {"ok": False, "error": f"early-bird: {inj.get('error')}; fallback: {retry.get('error')}"}
                        else:
                            result = {"ok": False, "error": inj.get("error") or "early-bird failed"}

            if not result.get("ok") and force_old:
                # Try normal launch + ClientVersion patch
                launch = _launch_normal(target["exe"])
                if not launch.get("ok"):
                    return {"ok": False, "error": launch.get("error") or "launch failed"}
                pid = launch["pid"]
                self._pre_inject(pid, target["name"])
                # Wait for the client to spin up
                deadline = time.time() + int(rb.get("injectTimeoutSec", 60))
                while time.time() < deadline:
                    if pid in self._get_roblox_pids():
                        break
                    time.sleep(0.5)
                time.sleep(1.5)

                if use_version_patch:
                    try:
                        newest = installed[0]["name"]
                        if target["name"] != newest:
                            patch_client_version_string(pid, newest)
                    except Exception:
                        pass

                retry = self._do_inject(pid, "loadlibrary")
                if retry.get("ok"):
                    result = {
                        "ok": True, "attached": True, "pid": pid,
                        "message": f"Launched + injected into {target['name']}",
                        "method": "loadlibrary", "version": target["name"],
                        "dll": str(dll),
                    }
                else:
                    result = {"ok": False, "error": retry.get("error") or "inject failed"}

            return result

    def simulate_execute(self, payload):
        code = str(payload.get("code") or "").strip()
        title = str(payload.get("title") or "Untitled")
        if not code: return {"ok": False, "error": "Script buffer is empty"}
        try:
            conn = socket.create_connection((EXEC_HOST, EXEC_PORT), timeout=5)
            conn.sendall(struct.pack("!I", len(code.encode("utf-8"))) + code.encode("utf-8"))
            conn.close()
            return {"ok": True, "title": title, "lines": len(code.splitlines()), "bytes": len(code)}
        except OSError as e:
            return {"ok": False, "error": f"Module not attached ({e})"}

    # ── Window controls ───────────────────────────────────────────────────
    def window_minimize(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            try: _main_window.minimize()
            except Exception: pass
        return {"ok": True}

    def window_maximize(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            try:
                if self.is_maximized: _main_window.restore(); self.is_maximized = False
                else: _main_window.maximize(); self.is_maximized = True
            except Exception: pass
        else: self.is_maximized = not self.is_maximized
        return {"ok": True, "maximized": self.is_maximized}

    def window_resize(self, payload):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False}
        try:
            w = int(payload.get("width") or 0); h = int(payload.get("height") or 0)
            if w < 400 or h < 300: return {"ok": False}
            try: _main_window.resize(w, h)
            except AttributeError: pass
            return {"ok": True}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def window_get_rect(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False}
        try:
            return {"ok": True, "width": int(_main_window.width or 0), "height": int(_main_window.height or 0)}
        except Exception as exc: return {"ok": False, "error": str(exc)}

    def window_close(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            if self.settings.get("general", {}).get("minimizeToTray") and _tray_icon is not None:
                toggle_window_visibility(); return {"ok": True, "hidToTray": True}
            try: _main_window.destroy()
            except Exception: pass
        return {"ok": True}


# ═══════════════════════════════════════════════════════════════════════════════
#  FRONTEND
# ═══════════════════════════════════════════════════════════════════════════════

KITTY_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Kitty</title>
<style>
:root{
--bg:#f4ede1;--panel:#eae2d2;--surface:#ddd3bf;--elevated:#cfc4ad;--hover:#c3b69b;
--overlay:rgba(20,20,25,0.72);--border:#d6cbb6;--border-strong:#b3a586;--divider:#e0d6c2;
--text:#141419;--text2:#41414d;--text3:#7a7a88;
--accent:#1e3a5f;--accent-hover:#2f5f92;--accent-soft:rgba(30,58,95,0.16);--accent2:#2f5f92;
--glow:rgba(30,58,95,0.20);--selection:rgba(30,58,95,0.22);
--success:#2d8659;--warn:#b87333;--danger:#a83232;--info:#2f5f92;
--r-xs:2px;--r-sm:4px;--r-md:6px;--r-lg:8px;--r-xl:12px;
--s-1:2px;--s-2:4px;--s-3:6px;--s-4:8px;--s-5:10px;--s-6:12px;--s-7:14px;--s-8:16px;--s-9:20px;--s-10:24px;--s-11:32px;--s-12:40px;
--h-row:24px;--h-control:26px;--h-titlebar:34px;--h-status:22px;--h-tabbar:32px;
--font-ui:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
--font-editor:'Cascadia Code','JetBrains Mono','Fira Code',Consolas,ui-monospace,monospace;
--fs-xs:9px;--fs-sm:10px;--fs-base:11px;--fs-md:12px;--fs-lg:13px;--fs-xl:15px;
--editor-size:13px;--editor-weight:400;--editor-lh:1.55;
--dur-fast:90ms;--dur:150ms;--dur-slow:240ms;--dur-cinematic:380ms;
--ease-out:cubic-bezier(0.2,0.9,0.3,1);--ease-spring:cubic-bezier(0.34,1.56,0.64,1);--ease-spring-soft:cubic-bezier(0.2,1.15,0.35,1);
--activity-w:44px;--explorer-w:240px;--rail-w:40px;
--bg-img-opacity:0;--bg-img-blur:4px;--bg-img-sat:100%;--bg-img-size:cover;--bg-img-pos:center center;
--panel-opacity:0.82;--spotlight-opacity:0;
--fx-opacity:0.55;--fx-color:var(--accent);--fx-color-2:var(--accent2);--fx-blur:70px;
--border-color:transparent;--border-width:2px;
--scroll-thumb:color-mix(in srgb,var(--text3) 35%,transparent);
--scroll-thumb-hover:color-mix(in srgb,var(--text3) 65%,transparent);
}
body[data-density="compact"]{--h-row:22px;--h-control:24px;}
body[data-density="comfortable"]{--h-row:26px;--h-control:28px;}
body[data-density="spacious"]{--h-row:30px;--h-control:32px;}
body[data-radius="sharp"]{--r-xs:0;--r-sm:0;--r-md:1px;--r-lg:2px;--r-xl:3px;}
body[data-radius="rounded"]{--r-xs:4px;--r-sm:7px;--r-md:10px;--r-lg:14px;--r-xl:18px;}
body[data-speed="slow"]{--dur-fast:160ms;--dur:260ms;--dur-slow:380ms;}
body[data-speed="fast"]{--dur-fast:55ms;--dur:90ms;--dur-slow:150ms;}
body.reduce-motion *,body.no-animations *{transition-duration:0ms!important;animation-duration:0ms!important;}
body.no-glow *{box-shadow:none!important;}
body.no-hover *:hover{transform:none!important;}
body.no-press *:active{transform:none!important;}
body.hide-sidebar-labels .tree-item>span{visibility:hidden;}

*{margin:0;padding:0;box-sizing:border-box;}
*::selection{background:var(--selection);color:var(--text);}
html,body{width:100%;height:100%;overflow:hidden;color:var(--text);font-family:var(--font-ui);font-size:var(--fs-base);-webkit-font-smoothing:antialiased;user-select:none;-webkit-user-select:none;}
body{background:var(--bg);}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer;position:relative;overflow:hidden;}
button:disabled{cursor:not-allowed;opacity:0.5;}
input,select,textarea{font:inherit;color:inherit;}
svg{display:block;}
::-webkit-scrollbar{width:12px;height:12px;background:transparent;}
::-webkit-scrollbar-thumb{background:var(--scroll-thumb);border-radius:8px;border:3px solid transparent;background-clip:padding-box;}
::-webkit-scrollbar-thumb:hover{background:var(--scroll-thumb-hover);border:2px solid transparent;background-clip:padding-box;}
*:focus-visible{outline:1px solid var(--accent);outline-offset:1px;border-radius:var(--r-sm);}

#wallpaper{position:fixed;inset:0;z-index:1;pointer-events:none;background-size:var(--bg-img-size);background-position:var(--bg-img-pos);background-repeat:no-repeat;opacity:var(--bg-img-opacity);filter:blur(var(--bg-img-blur)) saturate(var(--bg-img-sat));transition:opacity var(--dur-cinematic) var(--ease-out);}
body[data-bg-scope="editor"] #wallpaper{display:none;}
#bg-fx{position:fixed;inset:0;z-index:2;pointer-events:none;overflow:hidden;opacity:var(--fx-opacity);}
body.fx-off #bg-fx{opacity:0!important;}
.fx-orb{position:absolute;border-radius:50%;filter:blur(var(--fx-blur));background:radial-gradient(circle,var(--fx-color),transparent 70%);animation:orbDrift ease-in-out infinite;}
@keyframes orbDrift{0%,100%{transform:translate(0,0) scale(1);opacity:0.5;}33%{transform:translate(40px,-50px) scale(1.15);opacity:0.9;}66%{transform:translate(-30px,40px) scale(0.9);opacity:0.6;}}
.fx-spark{position:absolute;bottom:-10px;width:2.5px;height:2.5px;border-radius:50%;background:var(--fx-color);box-shadow:0 0 8px var(--fx-color);animation:sparkRise linear infinite;opacity:0;}
@keyframes sparkRise{0%{transform:translateY(0) scale(0);opacity:0;}15%{opacity:1;}85%{opacity:1;}100%{transform:translateY(-105vh) scale(1);opacity:0;}}
.fx-aurora-band{position:absolute;left:-20%;right:-20%;height:40vh;background:linear-gradient(120deg,transparent,color-mix(in srgb,var(--fx-color) 45%,transparent) 30%,color-mix(in srgb,var(--fx-color-2) 35%,transparent) 55%,transparent 90%);filter:blur(60px);border-radius:50%;opacity:0.35;animation:auroraSway 18s ease-in-out infinite;}
@keyframes auroraSway{0%,100%{transform:translateX(-15%) rotate(-4deg);opacity:0.25;}50%{transform:translateX(15%) rotate(4deg);opacity:0.55;}}
#spotlight{position:fixed;inset:0;z-index:3;pointer-events:none;opacity:var(--spotlight-opacity);background:radial-gradient(360px circle at var(--cx,-500px) var(--cy,-500px),var(--glow),transparent 70%);}
#water-canvas{position:fixed;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;opacity:.78;mix-blend-mode:screen;}

@keyframes fogBreathe{0%,100%{box-shadow:0 0 0 0 transparent,0 0 5px color-mix(in srgb,var(--accent) 10%,transparent);}50%{box-shadow:0 0 0 1px color-mix(in srgb,var(--accent) 20%,transparent),0 0 17px color-mix(in srgb,var(--accent) 29%,transparent);}}
body.fog-glow button:hover,body.fog-glow .act-btn:hover,body.fog-glow .nav-icon:hover,body.fog-glow .tree-item:hover{animation:fogBreathe 2.7s ease-in-out infinite;border-color:var(--accent);}

.click-particle{position:fixed;width:6px;height:6px;border-radius:50%;pointer-events:none;z-index:99999;background:var(--accent);animation:clickParticle 700ms var(--ease-out) forwards;}
@keyframes clickParticle{from{transform:translate(-50%,-50%) scale(1);opacity:1;}to{transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) scale(0);opacity:0;}}
.trail-dot{position:fixed;width:8px;height:8px;border-radius:50%;background:var(--accent);pointer-events:none;z-index:99998;transform:translate(-50%,-50%);animation:trailFade 500ms var(--ease-out) forwards;}
@keyframes trailFade{from{transform:translate(-50%,-50%) scale(1);opacity:0.6;}to{transform:translate(-50%,-50%) scale(0.2);opacity:0;}}

#app{position:relative;z-index:5;width:100vw;height:100vh;display:flex;flex-direction:column;background:transparent;}
#border-layer{position:fixed;inset:0;z-index:9999;pointer-events:none;display:none;}
body.border-on #border-layer{display:block;}
body.border-rainbow #border-layer{background:linear-gradient(120deg,#ff0066,#ffcc00,#00e676,#00b0ff,#b388ff,#ec4899,#ff0066);background-size:400% 400%;animation:borderShift 8s linear infinite;opacity:0.85;}
body.border-solid #border-layer{background:var(--border-color);opacity:0.9;}
body.border-on #border-layer{-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);mask-composite:exclude;padding:var(--border-width);}
@keyframes borderShift{0%{background-position:0% 50%;}100%{background-position:400% 50%;}}

#titlebar{position:relative;z-index:10;height:var(--h-titlebar);min-height:var(--h-titlebar);display:flex;align-items:center;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--divider);padding:0 var(--s-4) 0 var(--s-6);-webkit-app-region:drag;overflow:hidden;}
#topo-layer{position:absolute;inset:0;pointer-events:none;opacity:0.10;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='44'%3E%3Cpath d='M180 -10 C210 10, 260 8, 290 20 C320 32, 370 26, 410 40' fill='none' stroke='%23888' stroke-width='1'/%3E%3C/svg%3E");background-repeat:repeat-x;color:var(--text3);}
body.no-topo #topo-layer{opacity:0;}
#titlebar .tb-left{display:flex;align-items:center;gap:var(--s-4);z-index:2;}
.brand{display:flex;align-items:center;gap:var(--s-4);color:var(--text);font-size:var(--fs-md);font-weight:600;}
.brand-logo{min-width:26px;height:26px;color:var(--accent);display:inline-flex;align-items:center;justify-content:center;}
.brand-logo svg{width:22px;height:22px;display:block;}
.brand-name{font-family:'Brush Script MT','Segoe Script','Lucida Handwriting',cursive;font-size:19px;font-weight:400;letter-spacing:-0.4px;font-style:italic;color:var(--text);line-height:1;}
body.reaper-mode .brand-name{font-family:var(--font-editor);font-style:normal;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;}
.brand-ver{font-size:var(--fs-sm);color:var(--text3);padding:1px 5px;border:1px solid var(--border);border-radius:var(--r-sm);letter-spacing:0.04em;font-family:var(--font-editor);}
.tb-center{position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:var(--s-1);padding:2px;border-radius:var(--r-md);z-index:2;background:color-mix(in srgb,var(--surface) 80%,transparent);border:1px solid var(--divider);}
.nav-icon{width:30px;height:22px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;color:var(--text3);transition:color var(--dur),background var(--dur),transform var(--dur-fast) var(--ease-spring);position:relative;}
.nav-icon svg{width:14px;height:14px;stroke:currentColor;stroke-width:1.75;fill:none;}
.nav-icon:hover{color:var(--text2);background:var(--surface);transform:translateY(-1px);}
.nav-icon.active{color:var(--text);background:var(--surface);}
.nav-icon.active::after{content:"";position:absolute;left:6px;right:6px;bottom:-3px;height:2px;background:var(--accent);border-radius:2px;}
.tb-right{margin-left:auto;display:flex;align-items:center;gap:2px;z-index:2;}
.wbtn{width:34px;height:26px;display:inline-flex;align-items:center;justify-content:center;color:var(--text2);border-radius:var(--r-sm);transition:background var(--dur),color var(--dur);}
.wbtn svg{width:11px;height:11px;stroke:currentColor;stroke-width:1.4;fill:none;}
.wbtn:hover{background:var(--surface);color:var(--text);}
.wbtn.close:hover{background:#c42b1c;color:#fff;}

#body{flex:1;min-height:0;display:flex;position:relative;z-index:2;}
#activity{width:var(--activity-w);min-width:var(--activity-w);background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);backdrop-filter:blur(6px);border-right:1px solid var(--divider);display:flex;flex-direction:column;align-items:center;padding:var(--s-4) 0;gap:var(--s-1);}
#activity.hidden{display:none;}
.act-btn{width:30px;height:30px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);border-radius:var(--r-sm);position:relative;transition:color var(--dur),background var(--dur),transform var(--dur-fast);}
.act-btn svg{width:15px;height:15px;stroke:currentColor;stroke-width:1.7;fill:none;}
.act-btn:hover{color:var(--text2);background:var(--surface);}
.act-btn.active{color:var(--text);background:var(--surface);}
.act-btn.active::before{content:"";position:absolute;left:-8px;top:6px;bottom:6px;width:2px;background:var(--accent);border-radius:2px;}
.act-sep{flex:1;}
.act-bottom{display:flex;flex-direction:column;gap:var(--s-1);}

#explorer{width:var(--explorer-w);min-width:0;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);backdrop-filter:blur(6px);border-right:1px solid var(--divider);display:flex;flex-direction:column;transition:width var(--dur-slow) var(--ease-spring-soft),opacity var(--dur),border-right-color var(--dur);overflow:hidden;}
#explorer.hidden{width:0;min-width:0;opacity:0;border-right-color:transparent;pointer-events:none;}
.explorer-head{height:var(--h-tabbar);min-height:var(--h-tabbar);padding:0 var(--s-4) 0 var(--s-5);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);gap:var(--s-3);}
.explorer-title{font-size:var(--fs-sm);font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);}
.explorer-head-actions{display:flex;gap:2px;align-items:center;}
.explorer-collapse{width:22px;height:22px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;color:var(--text3);transition:all var(--dur);}
.explorer-collapse:hover{background:var(--surface);color:var(--text);}
.explorer-collapse svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2;}
.explorer-body{flex:1;overflow-y:auto;overflow-x:hidden;min-height:0;}

.field{display:flex;align-items:center;gap:var(--s-3);height:var(--h-control);background:var(--bg);border:1px solid var(--divider);border-radius:var(--r-sm);padding:0 var(--s-4);transition:border-color var(--dur);}
.field:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px var(--glow);}
.field svg{width:12px;height:12px;color:var(--text3);stroke:currentColor;fill:none;stroke-width:1.8;flex-shrink:0;}
.field input{flex:1;background:transparent;border:none;outline:none;font-size:var(--fs-base);color:var(--text);min-width:0;}

.panel-section{padding:var(--s-4);}
.panel-section .p-head{font-size:var(--fs-sm);font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);margin-bottom:var(--s-3);display:flex;align-items:center;gap:var(--s-3);}
.panel-section .p-head::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--divider),transparent);}
.p-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:var(--s-4) var(--s-5);margin-bottom:var(--s-3);font-size:var(--fs-base);color:var(--text2);}
.p-card strong{color:var(--text);font-weight:600;display:block;margin-bottom:2px;}
.p-card .meta{font-size:var(--fs-sm);color:var(--text3);}

.tree-group{margin-bottom:var(--s-4);padding:0 var(--s-3);}
.tree-group-head{display:flex;align-items:center;gap:var(--s-2);padding:var(--s-2) var(--s-3);color:var(--text3);font-size:var(--fs-sm);font-weight:700;text-transform:uppercase;letter-spacing:0.06em;cursor:pointer;border-radius:var(--r-sm);}
.tree-group-head:hover{color:var(--text2);}
.tree-group-head svg{width:9px;height:9px;stroke:currentColor;fill:none;stroke-width:2;transition:transform var(--dur-slow);}
.tree-group[data-open="false"] .tree-group-head svg{transform:rotate(-90deg);}
.tree-group[data-open="false"] .tree-items{max-height:0;opacity:0;padding:0;}
.tree-group-count{margin-left:auto;color:var(--text3);font-size:var(--fs-xs);background:var(--bg);padding:1px 5px;border-radius:8px;}
.tree-items{display:flex;flex-direction:column;gap:1px;padding-left:var(--s-5);overflow:hidden;max-height:900px;transition:max-height var(--dur-slow) var(--ease-spring-soft),opacity var(--dur),padding var(--dur);}
.tree-item{display:flex;align-items:center;gap:7px;min-height:var(--h-row,22px);height:var(--h-row,22px);padding:0 7px;border-radius:var(--r-sm);color:var(--text2);font-size:11px;line-height:1;cursor:pointer;position:relative;white-space:nowrap;overflow:hidden;transition:background var(--dur),color var(--dur),transform var(--dur-fast);}
.tree-item:hover{background:var(--surface);color:var(--text);transform:translateX(2px);}
.tree-item.active{background:var(--surface);color:var(--text);}
.tree-item.active::before{content:"";position:absolute;left:-6px;top:5px;bottom:5px;width:2px;background:var(--accent);border-radius:2px;}
.tree-item>svg{width:14px;height:14px;min-width:14px;flex:0 0 14px;color:var(--text3);}
.tree-item>span{flex:1 1 auto;min-width:0;display:block;color:inherit;font-size:inherit;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.tree-item-state{margin-left:auto;font-size:8px;color:var(--warn);border:1px solid color-mix(in srgb,var(--warn) 35%,transparent);padding:1px 4px;border-radius:4px;}

.logo-gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px;margin-top:8px;}
.logo-card{padding:14px 10px;border-radius:var(--r-md);background:var(--bg);border:1px solid var(--border);display:flex;flex-direction:column;align-items:center;gap:8px;cursor:pointer;transition:border-color var(--dur),transform var(--dur-fast);}
.logo-card:hover{border-color:var(--border-strong);transform:translateY(-3px);}
.logo-card.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.logo-card svg{width:44px;height:44px;color:var(--text);}
.logo-card .logo-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);}
.logo-card.active .logo-label{color:var(--accent);}

#workspace{flex:1;min-width:0;display:flex;flex-direction:column;background:transparent;}

#view-home{flex:1;overflow-y:auto;padding:var(--s-11);display:none;flex-direction:column;gap:var(--s-9);}
#view-home.active{display:flex;}
#view-home .home-head{display:flex;align-items:center;gap:var(--s-6);margin-bottom:var(--s-3);}
#view-home .home-head-icon{min-width:52px;height:52px;padding:6px 10px;border-radius:var(--r-lg);display:inline-flex;align-items:center;justify-content:center;background:var(--surface);border:1px solid var(--border);color:var(--accent);}
#view-home .home-head-icon svg{width:26px;height:26px;}
#view-home .home-head-title{font-family:'Brush Script MT',cursive;font-size:28px;font-weight:400;color:var(--text);letter-spacing:-0.6px;font-style:italic;}
#view-home .home-head-sub{font-size:var(--fs-md);color:var(--text2);margin-top:2px;}
.home-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:var(--s-6);}
.home-card{background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);backdrop-filter:blur(6px);border:1px solid var(--border);border-radius:var(--r-md);padding:var(--s-6) var(--s-7);transition:border-color var(--dur),transform var(--dur-slow);}
.home-card:hover{border-color:var(--border-strong);transform:translateY(-3px);}
.home-card-head{display:flex;align-items:center;gap:var(--s-4);margin-bottom:var(--s-5);}
.home-card-icon{width:22px;height:22px;color:var(--accent);display:inline-flex;align-items:center;justify-content:center;}
.home-card-icon svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;}
.home-card-title{font-size:var(--fs-md);font-weight:600;color:var(--text);}
.home-card-row{display:flex;justify-content:space-between;padding:var(--s-3) 0;font-size:var(--fs-base);border-bottom:1px solid var(--divider);}
.home-card-row:last-child{border-bottom:none;}
.home-card-row .l{color:var(--text3);}
.home-card-row .v{color:var(--text);font-family:var(--font-editor);font-size:var(--fs-sm);}
.home-card-row .v.ok{color:var(--success);}
.home-actions{display:flex;gap:var(--s-4);flex-wrap:wrap;}
.home-action{display:flex;align-items:center;gap:var(--s-4);padding:var(--s-5) var(--s-6);background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);color:var(--text);font-size:var(--fs-base);transition:border-color var(--dur),background var(--dur),transform var(--dur-fast);}
.home-action:hover{border-color:var(--accent);background:var(--elevated);transform:translateY(-2px);}
.home-action svg{width:14px;height:14px;color:var(--accent);stroke:currentColor;fill:none;stroke-width:1.8;}

#view-editor{flex:1;min-height:0;display:none;flex-direction:column;}
#view-editor.active{display:flex;}
#tabstrip{height:var(--h-tabbar);min-height:var(--h-tabbar);display:flex;align-items:stretch;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border-bottom:1px solid var(--divider);overflow:hidden;}
#tabs{display:flex;align-items:stretch;flex:1;overflow-x:auto;}
.tab{display:inline-flex;align-items:center;gap:var(--s-4);padding:0 var(--s-5) 0 var(--s-6);height:100%;max-width:190px;min-width:0;color:var(--text3);font-size:var(--fs-base);border-right:1px solid var(--divider);cursor:pointer;position:relative;flex-shrink:0;transition:color var(--dur),background var(--dur);}
.tab:hover{color:var(--text2);background:var(--surface);}
.tab.active{color:var(--text);background:color-mix(in srgb,var(--bg) 90%,transparent);}
.tab.active::before{content:"";position:absolute;left:0;right:0;bottom:0;height:1.5px;background:var(--accent);}
.tab-quote{color:var(--text3);font-family:var(--font-editor);font-size:10px;font-weight:600;}
.tab.active .tab-quote{color:var(--accent);}
.tab-badge{display:inline-flex;align-items:center;justify-content:center;min-width:16px;height:14px;padding:0 4px;border-radius:8px;font-family:var(--font-editor);font-size:var(--fs-xs);font-weight:700;color:#fff;background:var(--accent);}
.tab-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tab-dirty{width:5px;height:5px;border-radius:50%;background:var(--accent);flex-shrink:0;display:none;}
.tab.dirty .tab-dirty{display:block;}
.tab-close{width:14px;height:14px;border-radius:3px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);flex-shrink:0;opacity:0;transition:opacity var(--dur),background var(--dur);}
.tab:hover .tab-close,.tab.active .tab-close{opacity:1;}
.tab-close:hover{background:var(--surface);color:var(--text);}
.tab-close svg{width:8px;height:8px;stroke:currentColor;fill:none;stroke-width:1.6;}
#tab-new{width:32px;height:100%;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);flex-shrink:0;}
#tab-new:hover{background:var(--surface);color:var(--text);}
#tab-new svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2;}
#tab-toolbar{display:flex;align-items:center;gap:var(--s-2);padding:0 var(--s-4);border-left:1px solid var(--divider);}
#tab-toolbar button{color:var(--text3);width:26px;height:22px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;transition:background var(--dur),color var(--dur);}
#tab-toolbar button svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.7;}
#tab-toolbar button:hover{background:var(--surface);color:var(--text);}
#tab-toolbar button.active{color:var(--accent);background:var(--surface);}

#editor-wrap{flex:1;min-height:0;display:flex;flex-direction:column;}
#editor-body{flex:1;min-height:0;display:flex;position:relative;}
#gutter{width:46px;min-width:46px;padding:10px 8px 10px 4px;color:var(--text3);font-family:var(--font-editor);font-size:var(--editor-size);line-height:var(--editor-lh);text-align:right;overflow:hidden;user-select:none;white-space:pre;}
#gutter.hidden{display:none;}
.gln{padding-right:2px;}
.gln.active{color:var(--text2);}
#editor-stage{flex:1;min-width:0;position:relative;overflow:hidden;}
#current-line{position:absolute;left:0;right:0;height:calc(var(--editor-size) * var(--editor-lh));border-top:1px solid color-mix(in srgb,var(--text) 4%,transparent);border-bottom:1px solid color-mix(in srgb,var(--text) 4%,transparent);background:color-mix(in srgb,var(--text) 1.5%,transparent);pointer-events:none;z-index:1;}
body.no-current-line #current-line{display:none;}
#syntax,#editor-input{position:absolute;inset:0;width:100%;height:100%;padding:10px 14px;margin:0;border:none;outline:none;font-family:var(--font-editor);font-size:var(--editor-size);font-weight:var(--editor-weight);line-height:var(--editor-lh);tab-size:4;white-space:pre;}
#syntax{z-index:2;pointer-events:none;color:var(--text);overflow:hidden;}
#editor-input{z-index:3;resize:none;background:transparent;color:transparent;caret-color:var(--text);user-select:text;}
#editor-input.word-wrap,#syntax.word-wrap{white-space:pre-wrap;}
.tk-kw{color:#c9303d;font-weight:600;}.tk-fn{color:#2f5f92;}.tk-str{color:#2d8659;}.tk-num{color:#b87333;}
.tk-com{color:var(--text3);font-style:italic;}
body[data-theme^="kitty"] .tk-kw{color:#1e3a5f;font-weight:600;}
body[data-theme^="kitty"] .tk-fn{color:#2f5f92;}
body[data-theme^="kitty"] .tk-str{color:#2d8659;}
body[data-theme^="kitty"] .tk-num{color:#b87333;}
#find-bar{position:absolute;top:8px;right:24px;z-index:30;background:var(--surface);border:1px solid var(--border-strong);border-radius:var(--r-md);padding:var(--s-4) var(--s-5);display:none;flex-direction:column;gap:var(--s-3);}
#find-bar.open{display:flex;}
.find-row{display:flex;align-items:center;gap:var(--s-3);}
.find-row input{width:180px;height:var(--h-control);background:var(--bg);border:1px solid var(--border);border-radius:var(--r-sm);padding:0 var(--s-4);color:var(--text);outline:none;}
.mini-btn{height:var(--h-control);padding:0 var(--s-4);background:var(--elevated);border:1px solid var(--border);border-radius:var(--r-sm);color:var(--text2);font-size:var(--fs-sm);}
.mini-btn:hover{color:var(--text);border-color:var(--border-strong);}

#bottom-panel{height:180px;min-height:80px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border-top:1px solid var(--divider);display:flex;flex-direction:column;}
#bottom-panel.hidden{height:0;min-height:0;overflow:hidden;border-top-color:transparent;}
#bottom-resizer{height:4px;cursor:ns-resize;background:transparent;display:flex;align-items:center;justify-content:center;}
#bottom-resizer:hover{background:var(--surface);}
#bottom-resizer::before{content:"";width:30px;height:2px;background:var(--border-strong);}
#bottom-resizer.hidden{display:none;}
#bottom-tabs{height:28px;padding:0 var(--s-5);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);}
.bottom-tabs-left{display:flex;gap:var(--s-5);height:100%;}
.btab{height:100%;display:inline-flex;align-items:center;gap:var(--s-3);font-size:var(--fs-base);color:var(--text3);border-bottom:1.5px solid transparent;padding:0 2px;cursor:pointer;}
.btab:hover{color:var(--text2);}
.btab.active{color:var(--text);border-bottom-color:var(--accent);}
.btab svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:1.8;}
.bottom-tabs-right{display:flex;gap:var(--s-2);}
.bottom-tabs-right button{padding:3px 8px;border-radius:var(--r-sm);color:var(--text3);font-size:var(--fs-sm);}
.bottom-tabs-right button:hover{background:var(--surface);color:var(--text);}
#bottom-body{flex:1;min-height:0;overflow-y:auto;padding:var(--s-4) var(--s-5);}
#bottom-body.logs{font-family:var(--font-editor);font-size:var(--fs-sm);line-height:1.55;user-select:text;}
.log-line{display:flex;gap:var(--s-4);padding:1px 0;}
.log-time{color:var(--text3);flex-shrink:0;}
.log-msg{color:var(--text2);word-break:break-word;}
.log-line.info .log-msg{color:var(--text);}.log-line.ok .log-msg{color:var(--success);}.log-line.warn .log-msg{color:var(--warn);}.log-line.err .log-msg{color:var(--danger);}
#bottom-body.empty{display:flex;align-items:center;justify-content:center;color:var(--text3);font-style:italic;}

#rail{width:var(--rail-w);min-width:var(--rail-w);background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border-left:1px solid var(--divider);display:flex;flex-direction:column;align-items:center;padding:var(--s-4) 0;gap:var(--s-3);}
#rail.hidden{display:none;}
.rail-btn{width:30px;height:30px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;color:var(--text3);position:relative;transition:color var(--dur),background var(--dur),transform var(--dur-fast);}
.rail-btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:1.7;}
.rail-btn:hover{color:var(--text);background:var(--surface);}
.rail-btn.primary{background:var(--accent);color:#fff;}
.rail-btn.primary:hover{background:var(--accent-hover);}
.rail-sep{width:22px;height:1px;background:var(--divider);}
.rail-spacer{flex:1;}

#statusbar{height:var(--h-status);background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border-top:1px solid var(--divider);display:flex;align-items:center;padding:0 var(--s-5);font-size:var(--fs-sm);color:var(--text3);gap:var(--s-5);position:relative;z-index:5;}
.sb-group{display:flex;align-items:center;gap:var(--s-5);}
.sb-spacer{flex:1;}
.sb-item{display:inline-flex;align-items:center;gap:5px;}
.sb-item svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:1.8;}
.sb-path{font-family:var(--font-editor);max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.sb-dot{width:6px;height:6px;border-radius:50%;background:var(--text3);}
.sb-dot.on{background:var(--success);box-shadow:0 0 6px var(--success);}
.sb-btn{padding:2px 6px;border-radius:var(--r-sm);color:var(--text3);font-size:var(--fs-sm);display:inline-flex;align-items:center;gap:4px;}
.sb-btn:hover{background:var(--surface);color:var(--text);}
.sb-btn svg{width:10px;height:10px;stroke:currentColor;fill:none;stroke-width:2;}
#inject-menu{position:absolute;bottom:calc(var(--h-status) + 4px);right:8px;min-width:200px;background:var(--surface);border:1px solid var(--border-strong);border-radius:var(--r-md);padding:var(--s-2);display:none;z-index:200;}
#inject-menu.open{display:block;}
.menu-row{display:flex;align-items:center;gap:var(--s-4);padding:var(--s-3) var(--s-5);border-radius:var(--r-sm);color:var(--text2);font-size:var(--fs-base);cursor:pointer;}
.menu-row svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.8;}
.menu-row:hover{background:var(--hover);color:var(--text);}
.menu-row.danger:hover{color:var(--danger);}

#view-settings{flex:1;min-height:0;display:none;}
#view-settings.active{display:flex;}
#settings{flex:1;display:flex;min-height:0;}
#settings-nav{width:220px;min-width:220px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border-right:1px solid var(--divider);padding:var(--s-6) var(--s-5);display:flex;flex-direction:column;gap:var(--s-5);overflow-y:auto;}
#settings-nav .s-head{display:flex;align-items:center;gap:var(--s-4);padding:0 var(--s-3) var(--s-4);}
#settings-nav .s-head button{width:22px;height:22px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;color:var(--text2);}
#settings-nav .s-head button:hover{background:var(--surface);color:var(--text);}
#settings-nav .s-head svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:2;}
#settings-nav .s-head .s-title{font-size:var(--fs-lg);font-weight:600;color:var(--text);}
.s-search{display:flex;align-items:center;gap:var(--s-3);height:var(--h-control);background:var(--bg);border:1px solid var(--divider);border-radius:var(--r-sm);padding:0 var(--s-4);}
.s-search:focus-within{border-color:var(--accent);}
.s-search svg{width:12px;height:12px;color:var(--text3);stroke:currentColor;fill:none;stroke-width:1.8;}
.s-search input{flex:1;background:transparent;border:none;outline:none;font-size:var(--fs-base);color:var(--text);min-width:0;}
#settings-cats{display:flex;flex-direction:column;gap:1px;}
.s-cat{display:flex;align-items:center;gap:var(--s-5);padding:var(--s-3) var(--s-4);border-radius:var(--r-sm);color:var(--text2);font-size:var(--fs-base);cursor:pointer;position:relative;text-align:left;width:100%;}
.s-cat svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:1.7;flex-shrink:0;}
.s-cat:hover{background:var(--surface);color:var(--text);}
.s-cat.active{background:var(--surface);color:var(--text);}
.s-cat.active::before{content:"";position:absolute;left:-2px;top:6px;bottom:6px;width:2px;background:var(--accent);border-radius:2px;}
.s-cat-name{flex:1;min-width:0;}
.s-cat.s-cat-secret{color:var(--accent);opacity:0.7;}
.s-cat.s-cat-secret::after{content:"✦";font-size:9px;color:var(--accent);}
#settings-body{flex:1;min-width:0;overflow-y:auto;padding:var(--s-9) var(--s-11);scroll-behavior:smooth;}
.s-section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:var(--s-6);margin-bottom:var(--s-8);padding-bottom:var(--s-6);border-bottom:1px solid var(--divider);position:relative;}
.s-section-head::after{content:"";position:absolute;bottom:-1px;left:0;width:60px;height:2px;background:linear-gradient(90deg,var(--accent),transparent);}
.s-section-title{font-size:var(--fs-xl);font-weight:600;color:var(--text);}
.s-section-sub{font-size:var(--fs-base);color:var(--text3);margin-top:3px;line-height:1.55;}
.s-subhead{font-size:var(--fs-sm);font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);margin:var(--s-8) 0 var(--s-4);display:flex;align-items:center;gap:10px;}
.s-subhead::after{content:"";flex:1;height:1px;background-image:linear-gradient(90deg,color-mix(in srgb,var(--accent) 40%,var(--divider)),transparent);}
.s-subhead:first-child{margin-top:0;}
.s-row{display:flex;align-items:center;justify-content:space-between;gap:var(--s-8);padding:var(--s-5) var(--s-6);background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity) * 100%),transparent);border:1px solid var(--border);border-radius:var(--r-md);margin-bottom:var(--s-3);}
.s-row:hover{border-color:var(--border-strong);}
.s-row-info{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1;}
.s-row-title{font-size:var(--fs-md);color:var(--text);font-weight:500;}
.s-row-desc{font-size:var(--fs-base);color:var(--text3);line-height:1.5;}
.s-row-control{display:flex;align-items:center;gap:var(--s-4);flex-shrink:0;}
.s-row.vertical{flex-direction:column;align-items:stretch;}
.s-row.vertical .s-row-control{justify-content:flex-start;}

.theme-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:var(--s-4);margin-top:var(--s-4);}
.theme-card{padding:var(--s-4) var(--s-5);border-radius:var(--r-md);border:1px solid var(--border);background:var(--bg);cursor:pointer;display:flex;flex-direction:column;gap:var(--s-3);position:relative;}
.theme-card:hover{border-color:var(--border-strong);}
.theme-card.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.theme-card-head{display:flex;align-items:center;justify-content:space-between;}
.theme-card-name{font-size:var(--fs-md);color:var(--text);font-weight:600;}
.theme-check{font-size:8px;font-weight:800;color:var(--text3);}
.theme-card.active .theme-check{color:var(--accent);}
.theme-dots{display:flex;gap:3px;}
.theme-dot{width:10px;height:10px;border-radius:3px;border:1px solid rgba(0,0,0,0.14);}
.theme-card-desc{font-size:var(--fs-sm);color:var(--text3);line-height:1.4;}

.bg-thumbs{display:flex;gap:var(--s-4);flex-wrap:wrap;margin-top:var(--s-4);}
.bg-thumb{width:74px;height:48px;border-radius:var(--r-sm);background:var(--bg);border:1px solid var(--border);cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--text3);overflow:hidden;position:relative;}
.bg-thumb:hover{border-color:var(--border-strong);}
.bg-thumb.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.bg-thumb img{width:100%;height:100%;object-fit:cover;}
.bg-thumb svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:1.8;}

.sw{width:34px;height:18px;border-radius:9px;position:relative;background:var(--surface);border:1px solid var(--border-strong);cursor:pointer;flex-shrink:0;}
.sw::after{content:"";position:absolute;top:1px;left:1px;width:14px;height:14px;border-radius:50%;background:var(--text3);transition:transform var(--dur),background var(--dur);}
.sw.on{background:var(--accent);border-color:var(--accent);}
.sw.on::after{transform:translateX(16px);background:#fff;}

.slider-wrap{display:flex;align-items:center;gap:var(--s-4);min-width:220px;}
input[type=range].slider{-webkit-appearance:none;appearance:none;width:140px;height:3px;border-radius:2px;background:var(--border-strong);outline:none;cursor:pointer;}
input[type=range].slider::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;border-radius:50%;background:var(--accent);border:2px solid var(--bg);}
.slider-val{min-width:46px;text-align:right;font-family:var(--font-editor);font-size:var(--fs-sm);color:var(--text2);}

.ui-select,.ui-text{height:var(--h-control);padding:0 var(--s-5);background:var(--bg);border:1px solid var(--border-strong);border-radius:var(--r-sm);color:var(--text);outline:none;min-width:130px;}
.ui-select:focus,.ui-text:focus{border-color:var(--accent);}
.ui-text.mono{font-family:var(--font-editor);}
input[type=color].mini-color{width:28px;height:26px;border:none;background:transparent;cursor:pointer;padding:0;}

.btn{height:var(--h-control);padding:0 var(--s-6);background:var(--elevated);border:1px solid var(--border-strong);border-radius:var(--r-sm);color:var(--text2);font-size:var(--fs-base);display:inline-flex;align-items:center;gap:var(--s-3);transition:background var(--dur),color var(--dur),border-color var(--dur);}
.btn svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:1.8;}
.btn:hover{background:var(--hover);color:var(--text);}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff;}
.btn.primary:hover{background:var(--accent-hover);border-color:var(--accent-hover);}
.btn.danger{color:var(--danger);}
.btn.danger:hover{background:color-mix(in srgb,var(--danger) 12%,transparent);border-color:var(--danger);}
.btn.success{background:var(--success);border-color:var(--success);color:#fff;}

.segmented{display:inline-flex;background:var(--bg);border:1px solid var(--border);border-radius:var(--r-md);padding:3px;gap:2px;}
.segmented button{background:transparent;border:none;color:var(--text3);padding:4px 10px;border-radius:var(--r-sm);font-size:var(--fs-sm);font-weight:600;cursor:pointer;}
.segmented button.active{background:var(--accent);color:#fff;}
.segmented button:not(.active):hover{color:var(--text);background:var(--surface);}

.version-list{display:flex;flex-direction:column;gap:6px;width:100%;margin-top:8px;}
.version-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r-md);}
.version-row .vinfo{display:flex;flex-direction:column;gap:2px;min-width:0;}
.version-row .vname{font-family:var(--font-editor);font-size:11px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.version-row .vmeta{font-size:9px;color:var(--text3);}
.version-row.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}

#cmd-back{position:fixed;inset:0;z-index:500;background:rgba(0,0,0,0.5);backdrop-filter:blur(3px);display:none;align-items:flex-start;justify-content:center;padding-top:90px;}
#cmd-back.open{display:flex;}
#cmd-modal{width:460px;background:var(--panel);border:1px solid var(--border-strong);border-radius:var(--r-lg);overflow:hidden;}
#cmd-input{width:100%;height:42px;padding:0 var(--s-6);background:var(--bg);border:none;border-bottom:1px solid var(--divider);color:var(--text);font-size:var(--fs-md);outline:none;}
#cmd-list{max-height:340px;overflow-y:auto;padding:var(--s-2);}
.cmd-row{padding:var(--s-3) var(--s-5);border-radius:var(--r-sm);display:flex;align-items:center;justify-content:space-between;color:var(--text2);font-size:var(--fs-md);cursor:pointer;}
.cmd-row:hover,.cmd-row.selected{background:var(--surface);color:var(--text);}
.cmd-kb{font-family:var(--font-editor);font-size:var(--fs-sm);color:var(--text3);}
.cmd-cat{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);padding:var(--s-2) var(--s-5) var(--s-1);}

#tab-ctx,#file-ctx{position:fixed;z-index:620;min-width:170px;background:var(--panel);border:1px solid var(--border-strong);border-radius:var(--r-md);padding:var(--s-2);display:none;}
#tab-ctx.open,#file-ctx.open{display:block;}
.ctx-row{padding:var(--s-3) var(--s-5);border-radius:var(--r-sm);color:var(--text2);font-size:var(--fs-base);cursor:pointer;}
.ctx-row:hover{background:var(--hover);color:var(--text);}
.ctx-row.danger:hover{color:var(--danger);}
.ctx-sep{height:1px;background:var(--divider);margin:var(--s-2) 0;}

#app-modal-back{position:fixed;inset:0;z-index:10020;display:flex;align-items:center;justify-content:center;padding:22px;background:rgba(2,4,8,.58);backdrop-filter:blur(8px);opacity:0;visibility:hidden;pointer-events:none;transition:opacity var(--dur-slow);}
#app-modal-back.open{opacity:1;visibility:visible;pointer-events:auto;}
#app-modal{width:min(430px,calc(100vw - 34px));background:var(--panel);border:1px solid var(--border-strong);border-radius:var(--r-xl);overflow:hidden;}
#app-modal-head{padding:18px 20px 12px;display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--divider);}
#app-modal-mark{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);}
#app-modal-title{font-size:14px;font-weight:700;color:var(--text);}
#app-modal-message{padding:16px 20px 8px;color:var(--text2);font-size:12px;line-height:1.65;white-space:pre-wrap;}
#app-modal-input{display:block;width:calc(100% - 40px);margin:10px 20px 16px;padding:10px 12px;border:1px solid var(--border-strong);border-radius:var(--r-md);background:var(--bg);color:var(--text);outline:none;}
#app-modal-input:focus{border-color:var(--accent);}
#app-modal-actions{display:flex;justify-content:flex-end;gap:8px;padding:8px 20px 18px;}

#clients-backdrop{position:fixed;inset:0;z-index:640;background:rgba(0,0,0,0.55);opacity:0;pointer-events:none;transition:opacity var(--dur-slow);}
#clients-backdrop.open{opacity:1;pointer-events:auto;}
#clients{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:90vw;background:var(--panel);border-left:1px solid var(--border-strong);z-index:650;display:flex;flex-direction:column;transform:translateX(100%);transition:transform var(--dur-cinematic);}
#clients.open{transform:translateX(0);}
#clients .head{padding:var(--s-6) var(--s-7);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);}
#clients .title{font-size:var(--fs-lg);font-weight:600;color:var(--text);display:flex;align-items:center;gap:var(--s-4);}
#clients .close{width:26px;height:26px;border-radius:var(--r-sm);display:inline-flex;align-items:center;justify-content:center;color:var(--text2);}
#clients .close:hover{background:var(--surface);color:var(--text);}
#clients-list{flex:1;overflow-y:auto;padding:var(--s-5);}
.clients-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;gap:var(--s-5);padding:var(--s-9);color:var(--text3);}
.clients-empty h3{font-size:var(--fs-lg);color:var(--text2);font-weight:600;}
.client-row{display:flex;align-items:center;justify-content:space-between;padding:var(--s-5);background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);margin-bottom:var(--s-3);}
.client-info{display:flex;flex-direction:column;gap:2px;}
.client-pid{font-family:var(--font-editor);font-size:var(--fs-md);color:var(--text);}
.client-state{font-size:var(--fs-sm);color:var(--text3);}
.client-state.attached{color:var(--success);}
.client-attach{padding:5px 12px;background:var(--accent);color:#fff;border-radius:var(--r-sm);font-size:var(--fs-base);}
.client-attach:hover{background:var(--accent-hover);}
.client-attach:disabled{background:var(--border-strong);}

#attach-overlay{position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.55);display:none;align-items:center;justify-content:center;}
#attach-overlay.open{display:flex;}
.attach-box{background:var(--panel);border:1px solid var(--border-strong);border-radius:var(--r-lg);padding:var(--s-11);min-width:320px;text-align:center;}
.spinner{width:40px;height:40px;margin:0 auto var(--s-6);border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.9s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.attach-step{font-family:var(--font-editor);font-size:var(--fs-md);color:var(--text2);min-height:20px;}

#toasts{position:fixed;right:12px;bottom:34px;z-index:800;display:flex;flex-direction:column;gap:var(--s-3);pointer-events:none;}
.toast{pointer-events:auto;min-width:220px;max-width:320px;padding:var(--s-4) var(--s-6);background:var(--surface);border:1px solid var(--border-strong);border-radius:var(--r-md);display:flex;align-items:center;gap:var(--s-4);font-size:var(--fs-md);color:var(--text);}
.toast-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0;}
.toast.ok .toast-dot{background:var(--success);}.toast.warn .toast-dot{background:var(--warn);}.toast.err .toast-dot{background:var(--danger);}

#loading{position:fixed;inset:0;z-index:99999;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:var(--s-6);}
#loading.hidden{opacity:0;pointer-events:none;}
.load-logo{width:56px;height:56px;border-radius:50%;background:var(--surface);border:1px solid var(--border-strong);display:flex;align-items:center;justify-content:center;color:var(--accent);}
.load-logo svg{width:30px;height:30px;}
.load-title{font-family:'Brush Script MT',cursive;font-size:30px;color:var(--text);font-style:italic;}
.load-bar{width:180px;height:2px;background:var(--surface);border-radius:1px;overflow:hidden;}
.load-bar-fill{height:100%;width:0;background:var(--accent);}

#resize-grip{position:fixed;bottom:0;right:0;width:18px;height:18px;z-index:900;cursor:nwse-resize;display:flex;align-items:flex-end;justify-content:flex-end;padding:3px;color:var(--text3);opacity:0.6;}
#resize-grip:hover{opacity:1;color:var(--accent);}
#resize-grip svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2;}
</style>
</head>
<body data-radius="subtle" data-density="compact" data-speed="normal"
      data-syntax="crimson" data-bg-scope="whole" data-console-pos="bottom" data-theme="kitty">

<div id="wallpaper"></div>
<div id="bg-fx"></div>
<div id="spotlight"></div>
<canvas id="water-canvas"></canvas>
<div id="border-layer"></div>

<div id="loading">
  <div class="load-logo"><svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="16.6" rx="3.9" ry="2.9"/><ellipse cx="5.4" cy="10.1" rx="1.95" ry="2.4"/><ellipse cx="9.7" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="14.3" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="18.6" cy="10.1" rx="1.95" ry="2.4"/></svg></div>
  <div class="load-title">Kitty</div>
  <div class="load-bar"><div class="load-bar-fill" id="load-fill"></div></div>
</div>

<input type="file" id="pick-script" accept=".lua,.luau,.txt" style="display:none" />
<input type="file" id="pick-image" accept="image/png,image/jpeg,image/webp" style="display:none" />
<input type="file" id="pick-avatar" accept="image/png,image/jpeg,image/webp" style="display:none" />
<input type="file" id="pick-json" accept=".json" style="display:none" />

<div id="app">
  <header id="titlebar" class="pywebview-drag-region">
    <div id="topo-layer"></div>
    <div class="tb-left"><div class="brand"><span class="brand-logo" id="brand-logo"></span><span class="brand-name" id="brand-name">Kitty</span><span class="brand-ver" id="brand-ver">v4.6.0</span></div></div>
    <nav class="tb-center">
      <button class="nav-icon" data-tooltip="Home" data-view="home"><svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></button>
      <button class="nav-icon active" data-tooltip="Editor" data-view="editor"><svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></button>
      <button class="nav-icon" data-tooltip="Command Palette (Ctrl+K)" id="nav-cmd"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
      <button class="nav-icon" data-tooltip="Clients" id="nav-clients"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg></button>
      <button class="nav-icon" data-tooltip="Settings" data-view="settings"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 10v6M4.22 4.22l4.24 4.24m7.08 7.08l4.24 4.24M1 12h6m10 0h6"/></svg></button>
    </nav>
    <div class="tb-right">
      <button class="wbtn" id="win-min" title="Minimize"><svg viewBox="0 0 12 12"><line x1="2" y1="6" x2="10" y2="6"/></svg></button>
      <button class="wbtn" id="win-max" title="Maximize"><svg viewBox="0 0 12 12"><rect x="2" y="2" width="8" height="8"/></svg></button>
      <button class="wbtn close" id="win-close" title="Close"><svg viewBox="0 0 12 12"><line x1="2" y1="2" x2="10" y2="10"/><line x1="10" y1="2" x2="2" y2="10"/></svg></button>
    </div>
  </header>

  <div id="body">
    <aside id="activity">
      <button class="act-btn active" data-act="explorer" data-tooltip="Explorer"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3z"/><line x1="9" y1="3" x2="9" y2="21"/></svg></button>
      <button class="act-btn" data-act="search" data-tooltip="Search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
      <button class="act-btn" data-act="scripts" data-tooltip="Scripts"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></button>
      <button class="act-btn" data-act="autoexec" data-tooltip="Auto-Execute"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></button>
      <span class="act-sep"></span>
      <div class="act-bottom">
        <button class="act-btn" data-act="account" data-tooltip="Account"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></button>
      </div>
    </aside>

    <aside id="explorer">
      <div class="explorer-head">
        <span class="explorer-title" id="explorer-title">Explorer</span>
        <div class="explorer-head-actions">
          <button class="explorer-collapse" id="explorer-collapse" title="Collapse (Ctrl+B)"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>
        </div>
      </div>
      <div class="explorer-body" id="explorer-body"></div>
    </aside>

    <main id="workspace">
      <section id="view-home">
        <div class="home-head"><div class="home-head-icon" id="home-logo"></div><div><div class="home-head-title" id="home-title">Kitty</div><div class="home-head-sub" id="home-head-sub">v4.6.0 — premium workspace</div></div></div>
        <div class="home-grid">
          <div class="home-card"><div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></span><span class="home-card-title">Account</span></div><div class="home-card-row"><span class="l">User</span><span class="v" id="home-user">—</span></div><div class="home-card-row"><span class="l">Plan</span><span class="v" id="home-plan">—</span></div></div>
          <div class="home-card"><div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span><span class="home-card-title">License</span></div><div class="home-card-row"><span class="l">Status</span><span class="v ok" id="home-license">Active</span></div><div class="home-card-row"><span class="l">Expires</span><span class="v" id="home-expires">Never</span></div></div>
          <div class="home-card"><div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span><span class="home-card-title">Runtime</span></div><div class="home-card-row"><span class="l">DLL</span><span class="v" id="home-dll">—</span></div><div class="home-card-row"><span class="l">Offsets</span><span class="v" id="home-offsets">—</span></div><div class="home-card-row"><span class="l">Attached</span><span class="v" id="home-inject">Not injected</span></div></div>
          <div class="home-card"><div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span><span class="home-card-title">Versions</span></div><div class="home-card-row"><span class="l">Installed</span><span class="v" id="home-versions">—</span></div><div class="home-card-row"><span class="l">Newest</span><span class="v" id="home-newest">—</span></div></div>
        </div>
        <div class="home-card"><div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span><span class="home-card-title">Quick Actions</span></div><div class="home-actions">
          <button class="home-action" id="qa-new"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><span>New Script</span></button>
          <button class="home-action" id="qa-launch-inject"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Launch &amp; Inject</span></button>
          <button class="home-action" id="qa-attach"><svg viewBox="0 0 24 24"><path d="M18.36 6.64a9 9 0 1 1-12.72 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg><span>Attach</span></button>
          <button class="home-action" id="qa-settings"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/></svg><span>Settings</span></button>
        </div></div>
      </section>

      <section id="view-editor" class="active">
        <div id="tabstrip">
          <div id="tabs"></div>
          <button id="tab-new" title="New Tab (Ctrl+N)"><svg viewBox="0 0 24 24" fill="none"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></button>
          <div id="tab-toolbar">
            <button id="tb-open" title="Open File"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></button>
            <button id="tb-save" title="Save (Ctrl+S)"><svg viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/></svg></button>
            <button id="tb-find" title="Find (Ctrl+F)"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
            <button id="tb-replace" title="Replace (Ctrl+H)"><svg viewBox="0 0 24 24"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg></button>
            <button id="tb-copy" title="Copy All"><svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
          </div>
        </div>
        <div id="editor-body">
          <div id="gutter"></div>
          <div id="editor-stage">
            <div id="current-line"></div>
            <pre id="syntax" aria-hidden="true"></pre>
            <textarea id="editor-input" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea>
          </div>
          <div id="find-bar">
            <div class="find-row"><input type="text" id="find-input" placeholder="Find..." /><button class="mini-btn" id="find-next">Next</button><button class="mini-btn" id="find-close">✕</button></div>
            <div class="find-row" id="replace-row" style="display:none"><input type="text" id="replace-input" placeholder="Replace..." /><button class="mini-btn" id="replace-one">Replace</button><button class="mini-btn" id="replace-all">All</button></div>
          </div>
        </div>
        <div id="bottom-panel">
          <div id="bottom-resizer"></div>
          <div id="bottom-tabs">
            <div class="bottom-tabs-left">
              <button class="btab active" data-btab="terminal"><svg viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg><span>Terminal</span></button>
              <button class="btab" data-btab="roblox"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg><span>Roblox</span></button>
            </div>
            <div class="bottom-tabs-right"><button id="term-copy">Copy</button><button id="term-clear">Clear</button></div>
          </div>
          <div id="bottom-body" class="logs"></div>
        </div>
      </section>

      <section id="view-settings">
        <div id="settings">
          <aside id="settings-nav">
            <div class="s-head"><button id="settings-back" title="Back"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button><span class="s-title">Settings</span></div>
            <div class="s-search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="settings-search" placeholder="Search all settings..." /></div>
            <div id="settings-cats"></div>
          </aside>
          <div id="settings-body"></div>
        </div>
      </section>
    </main>

    <aside id="rail">
      <button class="rail-btn primary" id="rail-execute" data-tooltip="Execute"><svg viewBox="0 0 24 24" fill="none"><polygon points="6 4 20 12 6 20 6 4"/></svg></button>
      <span class="rail-sep"></span>
      <button class="rail-btn" id="rail-clear" data-tooltip="Clear editor"><svg viewBox="0 0 24 24"><path d="M20 20H7L3 16C2 15 2 13 3 12L13 2L22 11L20 20Z"/><line x1="6" y1="11" x2="13" y2="18"/></svg></button>
      <button class="rail-btn" id="rail-save" data-tooltip="Save"><svg viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/></svg></button>
      <button class="rail-btn" id="rail-open" data-tooltip="Open"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></button>
      <span class="rail-spacer"></span>
      <button class="rail-btn" id="rail-launch" data-tooltip="Launch &amp; Inject"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg></button>
      <button class="rail-btn" id="rail-inject" data-tooltip="Inject"><svg viewBox="0 0 24 24"><path d="M4 20l4-4"/><path d="M12 2l10 10-8 8-10-10z"/></svg></button>
    </aside>
  </div>

  <footer id="statusbar">
    <div class="sb-group"><span class="sb-item"><svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h18"/></svg><span class="sb-path" id="sb-path">No file</span></span></div>
    <span class="sb-spacer"></span>
    <div class="sb-group">
      <span class="sb-item" id="sb-cursor">Ln 1, Col 1</span>
      <span class="sb-item" id="sb-spaces">Spaces: 4</span>
      <span class="sb-item">UTF-8</span>
      <span class="sb-item" id="sb-version">—</span>
      <button class="sb-btn" id="inject-trigger"><span class="sb-dot" id="sb-dot"></span><span id="sb-inject-label">Not injected</span><svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg></button>
    </div>
  </footer>

  <div id="inject-menu">
    <div class="menu-row" id="menu-inject"><svg viewBox="0 0 24 24"><path d="M4 20l4-4"/><path d="M12 2l10 10-8 8-10-10z"/></svg><span>Inject (running)</span></div>
    <div class="menu-row" id="menu-launch-inject"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Launch &amp; Inject</span></div>
    <div class="menu-row" id="menu-clients"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg><span>Manage Clients</span></div>
    <div class="menu-row danger" id="menu-kill"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg><span>Kill Roblox</span></div>
  </div>
</div>

<div id="cmd-back"><div id="cmd-modal"><input type="text" id="cmd-input" placeholder="Type a command..." /><div id="cmd-list"></div></div></div>

<div id="app-modal-back" aria-hidden="true">
  <div id="app-modal">
    <div id="app-modal-head"><span id="app-modal-mark">✦</span><div id="app-modal-title">Kitty</div></div>
    <div id="app-modal-message"></div>
    <input id="app-modal-input" type="text" autocomplete="off" />
    <div id="app-modal-actions"><button class="btn" id="app-modal-cancel">Cancel</button><button class="btn primary" id="app-modal-ok">Save</button></div>
  </div>
</div>

<div id="tab-ctx">
  <div class="ctx-row" id="ctx-rename">Rename</div>
  <div class="ctx-row" id="ctx-dup">Duplicate</div>
  <div class="ctx-row" id="ctx-autoexec">Add to AutoExec</div>
  <div class="ctx-sep"></div>
  <div class="ctx-row" id="ctx-close-others">Close Others</div>
  <div class="ctx-row danger" id="ctx-close">Close</div>
</div>

<div id="file-ctx">
  <div class="ctx-row" id="file-ctx-open">Open</div>
  <div class="ctx-row" id="file-ctx-rename">Rename</div>
  <div class="ctx-sep"></div>
  <div class="ctx-row" id="file-ctx-disable">Disable Auto-Execute</div>
  <div class="ctx-row danger" id="file-ctx-remove">Remove File</div>
</div>

<div id="clients-backdrop"></div>
<div id="clients">
  <div class="head">
    <span class="title"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg> Roblox Clients</span>
    <button class="close" id="clients-close"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
  </div>
  <div id="clients-list"></div>
</div>

<div id="attach-overlay"><div class="attach-box"><div class="spinner"></div><div class="attach-step" id="attach-step">Preparing...</div></div></div>
<div id="toasts"></div>
<div id="resize-grip" title="Resize"><svg viewBox="0 0 24 24"><polyline points="21 15 21 21 15 21"/><polyline points="21 9 21 3 15 3"/><polyline points="9 21 3 21 3 15"/><polyline points="3 9 3 3 9 3"/></svg></div>

<script>
(() => {
"use strict";
const State = {
  booted:false, settings:null, builtinThemes:{}, app:{},
  scripts:[], tabs:[], closed:[], activeTab:null, ctxTab:null,
  attached:false, logs:{terminal:[],roblox:[]}, activeBottomTab:"terminal",
  pendingDataUrl:"", pendingFilename:"", pendingPalette:null,
  currentView:"editor", settingsSection:"roblox",
  explorerVisible:true, lastActivity:"explorer",
  dragTab:null, profilePicture:null, ctxFileId:null,
  offsets:null, versions:[], selectedVersion:"",
};

const LOGOS = {
  paw: { label:"Paw", svg:'<svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="16.6" rx="3.9" ry="2.9"/><ellipse cx="5.4" cy="10.1" rx="1.95" ry="2.4"/><ellipse cx="9.7" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="14.3" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="18.6" cy="10.1" rx="1.95" ry="2.4"/></svg>' },
  head: { label:"Cat Head", svg:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 4 L8 10 L12 8 L16 10 L19 4 L19 13 C19 17 16 20 12 20 C8 20 5 17 5 13 Z"/><circle cx="9.5" cy="13.2" r="0.9" fill="currentColor"/><circle cx="14.5" cy="13.2" r="0.9" fill="currentColor"/></svg>' },
  sit: { label:"Sitting", svg:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M8 7 L9.5 3.5 L11.5 6 L12.5 6 L14.5 3.5 L16 7 C15 9 15 11 15 13 C15 15.5 14 17 12 17 C10 17 9 15.5 9 13 C9 11 8 9 8 7 Z"/><path d="M9 17 C8 17 7 18 7 20 L7 21 L17 21 L17 20 C17 18 16 17 15 17"/></svg>' },
  tongue: { label:"Tongue", svg:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4 L8 10 L12 8 L16 10 L19 4 L19 13 C19 17 16 20 12 20 C8 20 5 17 5 13 Z"/><ellipse cx="10.8" cy="18.2" rx="1.6" ry="1.3" fill="#e8556d"/></svg>' },
  script: { label:"Script", svg:'<svg viewBox="0 0 24 24" fill="none"><text x="12" y="16.5" text-anchor="middle" font-family="Brush Script MT, cursive" font-size="13" font-style="italic" fill="currentColor">Kitty</text></svg>' },
};

const REAPER_SMALL = "☠";
const REAPER_BIG = "───── REAPER ─────";

const THEME_ICONS = {
  roblox:'<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/>',
  appearance:'<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>',
  behavior:'<circle cx="12" cy="12" r="3"/>',
  effects:'<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/>',
  editor:'<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  terminal:'<polyline points="4 17 10 11 4 5"/>',
  window:'<rect x="3" y="4" width="18" height="16" rx="2"/>',
  versions:'<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  connections:'<circle cx="12" cy="12" r="3"/>',
  secret:'<circle cx="12" cy="12" r="9"/>',
};

const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

async function api(method, payload={}) {
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api[method] === "function") {
    try { return await window.pywebview.api[method](payload); }
    catch (e) { console.error("[api]", method, e); return {ok:false, error:String(e)}; }
  }
  try {
    const r = await fetch(`/api/${method}`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    return await r.json();
  } catch (e) { return {ok:false, error:String(e)}; }
}

const animEnabled = () => State.settings?.effects?.masterAnimations !== false && State.settings?.effects?.reduceMotion !== true;

function themedDialog({ title="Kitty", message="", value="", confirmText="OK", cancelText="Cancel", danger=false, input=true } = {}) {
  return new Promise(resolve => {
    const back = $("#app-modal-back"), ti = $("#app-modal-title"), mi = $("#app-modal-message"),
          inp = $("#app-modal-input"), ok = $("#app-modal-ok"), ca = $("#app-modal-cancel");
    if (!back) { resolve(input ? null : false); return; }
    ti.textContent = title; mi.textContent = message;
    inp.style.display = input ? "block" : "none"; inp.value = value;
    ok.textContent = confirmText; ca.textContent = cancelText; ok.classList.toggle("danger", danger);
    back.classList.add("open");
    let done = false;
    const cleanup = (r) => {
      if (done) return; done = true;
      back.classList.remove("open");
      ok.removeEventListener("click", onOk); ca.removeEventListener("click", onCa);
      resolve(r);
    };
    const onOk = () => cleanup(input ? inp.value.trim() : true);
    const onCa = () => cleanup(input ? null : false);
    ok.addEventListener("click", onOk); ca.addEventListener("click", onCa);
    setTimeout(() => (input ? inp : ok).focus(), 30);
  });
}
const uiPrompt = (m, v="", t="Rename") => themedDialog({title:t, message:m, value:v, input:true});
const uiConfirm = (m, t="Confirm", c="Continue", d=false) => themedDialog({title:t, message:m, input:false, confirmText:c, danger:d});

function showToast(msg, level="info") {
  const s = $("#toasts"); if (!s) return;
  const el = document.createElement("div");
  el.className = `toast ${level}`;
  el.innerHTML = `<span class="toast-dot"></span><span>${esc(msg)}</span>`;
  s.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 3200);
}

function attachFxLayers() {
  // Ripples
  document.addEventListener("pointerdown", (e) => {
    if (!State.settings?.effects?.ripplesEnabled || !animEnabled()) return;
    const t = e.target.closest("button, .act-btn, .nav-icon, .rail-btn, .s-cat, .tab, .menu-row, .home-action, .theme-card, .tree-item");
    if (!t) return;
    const r = t.getBoundingClientRect();
    const size = Math.max(r.width, r.height);
    const rp = document.createElement("span");
    rp.style.cssText = `position:absolute;border-radius:50%;pointer-events:none;width:${size}px;height:${size}px;left:${e.clientX-r.left-size/2}px;top:${e.clientY-r.top-size/2}px;background:color-mix(in srgb,var(--accent) 38%,transparent);transform:scale(0);animation:clickParticle 600ms var(--ease-out) forwards;`;
    try { t.appendChild(rp); setTimeout(() => rp.remove(), 620); } catch(_) {}
  });
  // Click particles
  document.addEventListener("pointerdown", (e) => {
    if (!State.settings?.effects?.clickParticles || !animEnabled()) return;
    const N = Math.max(4, Math.min(36, Number(State.settings.effects.particleCount) || 16));
    const color = State.settings.effects.particleColor || getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
    for (let i = 0; i < N; i++) {
      const p = document.createElement("div"); p.className = "click-particle";
      const angle = (Math.PI * 2 * i) / N + Math.random() * 0.5;
      const dist = 24 + Math.random() * 70;
      p.style.left = e.clientX + "px"; p.style.top = e.clientY + "px";
      p.style.setProperty("--dx", Math.cos(angle) * dist + "px");
      p.style.setProperty("--dy", Math.sin(angle) * dist + "px");
      p.style.background = color;
      document.body.appendChild(p);
      setTimeout(() => p.remove(), 720);
    }
  });
  // Cursor trail
  let lastTrail = 0;
  window.addEventListener("pointermove", (e) => {
    if (!State.settings?.effects?.cursorTrail || !animEnabled()) return;
    const now = performance.now();
    if (now - lastTrail < Math.max(12, Math.min(100, Number(State.settings.effects.trailIntervalMs) || 42))) return;
    lastTrail = now;
    const color = State.settings.effects.particleColor || getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
    const dot = document.createElement("div"); dot.className = "trail-dot";
    dot.style.left = e.clientX + "px"; dot.style.top = e.clientY + "px";
    dot.style.background = color;
    document.body.appendChild(dot);
    setTimeout(() => dot.remove(), 520);
  });
  // Water cursor
  const canvas = $("#water-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  let ripples = [], raf = 0, lastMove = 0, lx = null, ly = null;
  const resize = () => {
    const dpr = Math.min(1.5, Math.max(1, window.devicePixelRatio || 1));
    canvas.width = innerWidth * dpr; canvas.height = innerHeight * dpr;
    canvas.style.width = innerWidth + "px"; canvas.style.height = innerHeight + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  const drop = (x, y, b=1) => {
    if (State.settings?.effects?.waterCursor === false || !animEnabled()) return;
    ripples.push({ x, y, t: performance.now(), b, s: Math.random() * 6.28 });
    if (ripples.length > 26) ripples.splice(0, ripples.length - 26);
    if (!raf) raf = requestAnimationFrame(draw);
  };
  const draw = (now) => {
    raf = 0;
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    if (State.settings?.effects?.waterCursor === false || !animEnabled()) { ripples = []; return; }
    const intensity = Math.max(1, Math.min(10, Number(State.settings.effects.waterIntensity) || 5)) / 5;
    const size = Math.max(24, Math.min(150, Number(State.settings.effects.waterSize) || 76));
    const hex = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim().replace("#","");
    const cl = /^[0-9a-f]{6}$/i.test(hex) ? hex : "52ff8a";
    const [rr, gg, bb] = [parseInt(cl.slice(0,2),16), parseInt(cl.slice(2,4),16), parseInt(cl.slice(4,6),16)];
    const keep = [];
    for (const w of ripples) {
      const p = (now - w.t) / (780 + size * 2.5);
      if (p >= 1) continue;
      keep.push(w);
      const fade = Math.pow(1 - p, 1.75) * Math.min(1.8, intensity) * w.b;
      const radius = 5 + p * size;
      ctx.save(); ctx.translate(w.x, w.y);
      ctx.globalCompositeOperation = "screen";
      for (let ring = 0; ring < 3; ring++) {
        const phase = Math.max(0, p - ring * .055);
        const rad = 7 + phase * size;
        ctx.beginPath();
        ctx.lineWidth = Math.max(.45, 1.45 - ring * .32);
        ctx.strokeStyle = `rgba(${rr},${gg},${bb},${fade * (.28 - ring * .055)})`;
        ctx.ellipse(0, 0, rad, rad * (.58 + ring * .04), 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
    }
    ripples = keep;
    if (ripples.length) raf = requestAnimationFrame(draw);
  };
  resize(); window.addEventListener("resize", resize);
  window.addEventListener("pointermove", (e) => {
    if (State.settings?.effects?.waterCursor === false || !animEnabled()) { lx = e.clientX; ly = e.clientY; return; }
    const now = performance.now();
    const dx = lx == null ? 0 : e.clientX - lx;
    const dy = ly == null ? 0 : e.clientY - ly;
    if (now - lastMove > 34 && (lx == null || dx*dx + dy*dy > 130)) { drop(e.clientX, e.clientY, .72); lastMove = now; }
    lx = e.clientX; ly = e.clientY;
  });
  window.addEventListener("pointerdown", e => drop(e.clientX, e.clientY, 1.18));
}

// Luau highlighter
const KW = /\b(local|function|return|if|then|elseif|else|end|for|in|do|while|repeat|until|and|or|not|true|false|nil|continue|break|export|type|typeof|self)\b/g;
const FN = /\b(print|warn|error|assert|pcall|require|pairs|ipairs|tostring|tonumber|loadstring|saveinstance|game|workspace|script|task|math|string|table|os|coroutine|Instance|Vector3|CFrame|Color3|UDim2)\b/g;
const NUM = /\b(0x[0-9a-fA-F]+|\d+(?:\.\d+)?)\b/g;

function highlight(code) {
  const lines = code.split("\n");
  return lines.map(line => {
    let comment = "";
    const ci = line.indexOf("--");
    if (ci !== -1) { comment = `<span class="tk-com">${esc(line.slice(ci))}</span>`; line = line.slice(0, ci); }
    const strings = [];
    line = line.replace(/(["'])(?:\\.|(?!\1).)*\1/g, (m) => {
      strings.push(`<span class="tk-str">${esc(m)}</span>`);
      return `\x00S${strings.length - 1}\x00`;
    });
    let safe = esc(line);
    safe = safe.replace(KW, '<span class="tk-kw">$1</span>');
    safe = safe.replace(FN, '<span class="tk-fn">$1</span>');
    safe = safe.replace(NUM, '<span class="tk-num">$1</span>');
    safe = safe.replace(/\x00S(\d+)\x00/g, (_, i) => strings[+i]);
    return safe + comment;
  }).join("\n") + "\n";
}

const hexToRgba = (hex, a) => {
  const h = (hex || "#000").replace("#","");
  return `rgba(${parseInt(h.slice(0,2),16)||0},${parseInt(h.slice(2,4),16)||0},${parseInt(h.slice(4,6),16)||0},${a})`;
};
const shade = (hex, f) => {
  const h = (hex || "#000000").replace("#","");
  const r = Math.min(255, Math.round((parseInt(h.slice(0,2),16)||0)*f));
  const g = Math.min(255, Math.round((parseInt(h.slice(2,4),16)||0)*f));
  const b = Math.min(255, Math.round((parseInt(h.slice(4,6),16)||0)*f));
  return `#${r.toString(16).padStart(2,"0")}${g.toString(16).padStart(2,"0")}${b.toString(16).padStart(2,"0")}`;
};

function renderBrandLogo() {
  if (!State.settings) return;
  const reaper = State.settings.secret?.reaperMode;
  const c = $("#brand-logo"), h = $("#home-logo");
  if (reaper) {
    if (c) c.innerHTML = `<span style="font-size:22px;line-height:1;">☠</span>`;
    if (h) h.innerHTML = `<span style="font-size:30px;line-height:1;">☠</span>`;
  } else {
    const id = State.settings.appearance.activeLogo || "paw";
    const l = LOGOS[id] || LOGOS.paw;
    if (c) c.innerHTML = l.svg;
    if (h) h.innerHTML = l.svg;
  }
}

function applyTheme() {
  if (!State.settings) return;
  const a = State.settings.appearance;
  const reaper = !!State.settings.secret?.reaperMode;
  let tid = a.theme;
  if (reaper && !tid.startsWith("reaper")) tid = "reaper";
  let pal = State.builtinThemes[tid];
  if (a.theme === "custom-colors" && !reaper) pal = { ...(State.builtinThemes.graphite||{}), ...(a.customColors||{}) };
  if (a.theme === "custom" && !reaper && a.imageAutoTheme !== false && a.customTheme?.palette) pal = a.customTheme.palette;
  if (!pal) pal = State.builtinThemes.kitty;
  document.body.setAttribute("data-theme", tid);
  const r = document.documentElement.style;
  for (const k of ["bg","panel","surface","elevated","hover","border","borderStrong","text","text2","text3"]) {
    if (pal[k]) r.setProperty("--" + (k === "borderStrong" ? "border-strong" : k), pal[k]);
  }
  if (pal.border) r.setProperty("--divider", pal.border);
  const acc = (!reaper && /^#[0-9a-fA-F]{6}$/.test(a.customAccentHex||"")) ? a.customAccentHex : pal.accent;
  r.setProperty("--accent", acc);
  r.setProperty("--accent2", pal.accent2 || acc);
  r.setProperty("--accent-hover", shade(acc, 1.15));
  r.setProperty("--accent-soft", hexToRgba(acc, 0.16));
  if (pal.glow) r.setProperty("--glow", pal.glow);
  if (pal.selection) r.setProperty("--selection", pal.selection);
  if (pal.success) r.setProperty("--success", pal.success);
  if (pal.warn) r.setProperty("--warn", pal.warn);
  if (pal.danger) r.setProperty("--danger", pal.danger);
  if (a.fxColorMode === "theme") {
    r.setProperty("--fx-color", acc); r.setProperty("--fx-color-2", pal.accent2 || acc);
  } else {
    r.setProperty("--fx-color", a.fxColor1 || acc); r.setProperty("--fx-color-2", a.fxColor2 || (pal.accent2 || acc));
  }
  renderBrandLogo();
}

function generateBgFx() {
  if (!State.settings) return;
  const a = State.settings.appearance;
  const layer = $("#bg-fx"); if (!layer) return;
  layer.innerHTML = "";
  if (a.fxType === "off") { document.body.classList.add("fx-off"); return; }
  document.body.classList.remove("fx-off");
  const n = { low:4, med:8, high:14 }[a.fxIntensity] || 8;
  if (a.fxType === "orbs") {
    for (let i = 0; i < n; i++) {
      const o = document.createElement("div"); o.className = "fx-orb";
      const sz = 140 + Math.random() * 260;
      o.style.cssText = `width:${sz}px;height:${sz}px;left:${Math.random()*100}%;top:${Math.random()*100}%;animation-duration:${10+Math.random()*12}s;animation-delay:-${Math.random()*12}s;`;
      layer.appendChild(o);
    }
  } else if (a.fxType === "sparkles") {
    for (let i = 0; i < n * 8; i++) {
      const s = document.createElement("div"); s.className = "fx-spark";
      s.style.cssText = `left:${Math.random()*100}%;animation-duration:${6+Math.random()*10}s;animation-delay:-${Math.random()*16}s;`;
      layer.appendChild(s);
    }
  } else if (a.fxType === "aurora") {
    for (let i = 0; i < 3; i++) {
      const b = document.createElement("div"); b.className = "fx-aurora-band";
      b.style.cssText = `top:${5+i*30}%;animation-delay:-${i*4}s;`;
      layer.appendChild(b);
    }
  }
}

function applySettings() {
  if (!State.settings) return;
  const { appearance:a, effects:e, editor:ed, console:c, general:g, secret:sec } = State.settings;
  const r = document.documentElement.style;
  document.body.setAttribute("data-density", a.uiDensity || "compact");
  document.body.setAttribute("data-radius", a.cornerRadius || "subtle");
  document.body.setAttribute("data-speed", e.animationSpeed || "normal");
  document.body.setAttribute("data-syntax", ed.syntaxTheme || "crimson");
  document.body.setAttribute("data-bg-scope", a.bgScope || "whole");
  document.body.setAttribute("data-console-pos", c.consolePosition || "bottom");
  document.body.classList.toggle("no-animations", !e.masterAnimations);
  document.body.classList.toggle("reduce-motion", !!e.reduceMotion);
  document.body.classList.toggle("show-indent-guides", !!ed.indentationGuides);
  document.body.classList.toggle("no-current-line", !ed.highlightCurrentLine);
  document.body.classList.toggle("no-glow", !e.glowEffects);
  document.body.classList.toggle("no-hover", !e.hoverEffects);
  document.body.classList.toggle("no-press", !e.buttonPressAnim);
  document.body.classList.toggle("no-topo", !a.topoHeaderPattern);
  document.body.classList.toggle("hide-sidebar-labels", a.sidebarLabels === false);
  document.body.classList.toggle("reaper-mode", !!sec?.reaperMode);
  document.body.classList.toggle("fog-glow", e.fogGlow !== false);

  const borderOn = a.borderEnabled !== false && a.borderMode !== "off";
  document.body.classList.toggle("border-on", borderOn);
  document.body.classList.toggle("border-rainbow", borderOn && a.borderMode === "rainbow");
  document.body.classList.toggle("border-solid", borderOn && a.borderMode === "solid");
  if (a.borderColor) r.setProperty("--border-color", a.borderColor);
  if (a.borderWidth) r.setProperty("--border-width", `${a.borderWidth}px`);

  const iconSize = Number(a.sidebarIconSize);
  r.setProperty("--sidebar-icon-size", (isFinite(iconSize) && iconSize > 0) ? `${iconSize}px` : "14px");

  const wp = $("#wallpaper");
  const imgUrl = a.customTheme?.imageDataUrl || "";
  if (a.useBackgroundImage && imgUrl) {
    wp.style.backgroundImage = `url("${imgUrl}")`;
    r.setProperty("--bg-img-opacity", (Number(a.bgImageOpacity||40)/100).toFixed(2));
    r.setProperty("--bg-img-blur", `${Number(a.bgImageBlur||4)}px`);
    r.setProperty("--bg-img-sat", `${Number(a.bgImageSaturation||100)}%`);
  } else {
    r.setProperty("--bg-img-opacity", "0"); wp.style.backgroundImage = "";
  }
  r.setProperty("--panel-opacity", (Number(a.panelOpacity||82)/100).toFixed(2));
  r.setProperty("--fx-opacity", { dim:"0.28", normal:"0.55", bold:"0.85" }[a.fxOpacity] || "0.55");
  generateBgFx();

  r.setProperty("--editor-size", `${Number(ed.fontSize||13)}px`);
  r.setProperty("--editor-lh", String(ed.lineHeight || 1.55));
  r.setProperty("--font-editor", `'${ed.fontFamily||"Cascadia Code"}', Consolas, monospace`);
  const inp = $("#editor-input"), syn = $("#syntax");
  if (inp) inp.style.tabSize = String(ed.tabSize || 4);
  if (syn) syn.style.tabSize = String(ed.tabSize || 4);
  inp?.classList.toggle("word-wrap", !!ed.wordWrap);
  syn?.classList.toggle("word-wrap", !!ed.wordWrap);
  $("#gutter")?.classList.toggle("hidden", !ed.lineNumbers);
  $("#sb-spaces").textContent = `Spaces: ${ed.tabSize || 4}`;

  $("#bottom-panel")?.classList.toggle("hidden", !c.showConsole);
  $("#bottom-resizer")?.classList.toggle("hidden", !c.showConsole);
  $("#rail")?.classList.toggle("hidden", !c.rightSidebarVisible);
  $("#activity")?.classList.toggle("hidden", !c.activityRailVisible);

  State.explorerVisible = c.leftExplorerVisible !== false;
  State.lastActivity = c.lastActivity || "explorer";
  syncExplorerVisibility();
  syncActivityActive();
  renderExplorerBody();

  $("#brand-name").textContent = sec?.reaperMode ? "REAPER" : (g.disguiseMode ? "Spotify" : "Kitty");
  $("#home-title").textContent = sec?.reaperMode ? "REAPER" : "Kitty";

  applyTheme();
  syncSettingsInputs();
  refreshEditor();
  renderLogs();
}

async function patchSettings(patch) {
  const res = await api("update_settings", patch);
  if (res && res.ok) {
    State.settings = res.settings;
    applyTheme(); applySettings();
  } else {
    showToast(res?.error || "Save failed", "err");
  }
}

// Explorer
function syncExplorerVisibility() {
  $("#explorer")?.classList.toggle("hidden", !State.explorerVisible);
}
function syncActivityActive() {
  const a = State.lastActivity || "explorer";
  $$(".act-btn").forEach(b => b.classList.toggle("active", b.dataset.act === a));
}
function handleActivityClick(name) {
  if (name === State.lastActivity && State.explorerVisible) State.explorerVisible = false;
  else { State.explorerVisible = true; State.lastActivity = name; }
  syncExplorerVisibility(); syncActivityActive(); renderExplorerBody();
  patchSettings({ console: { leftExplorerVisible: State.explorerVisible, lastActivity: name } });
}

function renderExplorerBody() {
  const body = $("#explorer-body"), title = $("#explorer-title");
  if (!body) return;
  const a = State.lastActivity || "explorer";
  title.textContent = ({ explorer:"Explorer", search:"Search", scripts:"Scripts", autoexec:"Auto-Execute", account:"Account" })[a] || "Explorer";
  if (a === "account") { body.innerHTML = renderAccountPanel(); wireAccountPanel(); return; }
  if (a === "search") { body.innerHTML = renderSearchPanel(); wireSearchPanel(); return; }
  const only = a === "scripts" ? "Scripts" : (a === "autoexec" ? "AutoExec" : "");
  body.innerHTML = renderFilesPanel(only);
  wireFilesPanel();
}

function renderFilesPanel(onlyFolder) {
  const groups = {};
  State.scripts.forEach(s => { (groups[s.folder||"Scripts"] = groups[s.folder||"Scripts"] || []).push(s); });
  ["Scripts","AutoExec"].forEach(f => groups[f] = groups[f] || []);
  let html = `<div class="panel-section" style="padding-bottom:6px"><div class="field"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="explorer-filter" placeholder="Filter files..." /></div></div>`;
  let any = false;
  Object.entries(groups).forEach(([name, items]) => {
    if (onlyFolder && name !== onlyFolder) return;
    if (!onlyFolder && items.length === 0) return;
    any = true;
    html += `<div class="tree-group" data-open="true" data-folder="${esc(name)}">
      <div class="tree-group-head"><svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg><span>${esc(name)}</span><span class="tree-group-count">${items.length}</span></div>
      <div class="tree-items">${items.map(s => `<div class="tree-item" data-id="${esc(s.id)}" data-title="${esc(s.title.toLowerCase())}"><svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M6 2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6H6z"/></svg><span>${esc(s.title)}</span>${s.disabled ? '<span class="tree-item-state">DISABLED</span>' : ""}</div>`).join("")}</div>
    </div>`;
  });
  if (!any) html += `<div class="panel-section"><div class="p-card"><strong>Empty</strong><div class="meta">No files here yet.</div></div></div>`;
  return html;
}
function wireFilesPanel() {
  $$("#explorer-body .tree-group-head").forEach(h => h.addEventListener("click", () => {
    const g = h.parentElement; g.dataset.open = g.dataset.open === "false" ? "true" : "false";
  }));
  $$("#explorer-body .tree-item").forEach(el => {
    el.addEventListener("click", () => {
      const s = State.scripts.find(x => x.id === el.dataset.id); if (s) openScript(s);
    });
    el.addEventListener("contextmenu", (ev) => {
      ev.preventDefault(); ev.stopPropagation();
      const s = State.scripts.find(x => x.id === el.dataset.id); if (!s) return;
      State.ctxFileId = s.id;
      const auto = (s.folder||"").toLowerCase().startsWith("autoexec");
      $("#file-ctx-rename").style.display = auto ? "none" : "";
      $("#file-ctx-disable").style.display = auto && !s.disabled ? "" : "none";
      const m = $("#file-ctx"); m.classList.add("open");
      m.style.left = Math.max(6, Math.min(ev.clientX, innerWidth - 205)) + "px";
      m.style.top = Math.max(6, Math.min(ev.clientY, innerHeight - 140)) + "px";
    });
  });
  const f = $("#explorer-filter");
  if (f) f.addEventListener("input", () => {
    const q = f.value.trim().toLowerCase();
    $$("#explorer-body .tree-item").forEach(el => el.style.display = (!q || (el.dataset.title||"").includes(q)) ? "" : "none");
  });
}
function renderSearchPanel() {
  return `<div class="panel-section"><div class="p-head">Search Scripts</div><div class="field" style="margin-bottom:10px"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/></svg><input type="text" id="side-search-input" placeholder="Find in name or content..." /></div><div id="side-search-results"></div></div>`;
}
function wireSearchPanel() {
  const inp = $("#side-search-input"), out = $("#side-search-results");
  if (!inp) return;
  const render = () => {
    const q = inp.value.trim().toLowerCase();
    out.innerHTML = "";
    if (!q) { out.innerHTML = `<div class="p-card"><div class="meta">Type to search.</div></div>`; return; }
    const m = State.scripts.filter(s => s.title.toLowerCase().includes(q) || (s.content||"").toLowerCase().includes(q));
    if (!m.length) { out.innerHTML = `<div class="p-card"><strong>No matches</strong></div>`; return; }
    m.slice(0, 40).forEach(s => {
      const row = document.createElement("div"); row.className = "p-card"; row.style.cursor = "pointer";
      row.innerHTML = `<strong>${esc(s.title)}</strong><div class="meta">${esc(s.folder||"Scripts")}</div>`;
      row.addEventListener("click", () => openScript(s));
      out.appendChild(row);
    });
  };
  inp.addEventListener("input", render); render();
}
function renderAccountPanel() {
  const g = State.settings.general;
  const pfp = State.profilePicture;
  const av = pfp ? `<img src="${pfp}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">` : LOGOS[State.settings.appearance.activeLogo]?.svg || LOGOS.paw.svg;
  return `<div class="panel-section">
    <div class="p-card" style="text-align:center">
      <div style="width:76px;height:76px;border-radius:50%;margin:0 auto 14px;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer" id="acct-avatar">${av}</div>
      <strong>${esc(g.userName||"—")}</strong>
      <div class="meta">${esc(g.planName||"Free")} · ${esc(g.licenseStatus||"Active")}</div>
      <div style="display:flex;gap:6px;margin-top:14px;justify-content:center">
        <button class="btn" id="acct-upload">Upload Avatar</button>
        <button class="btn danger" id="acct-remove">Remove</button>
      </div>
    </div>
    <div class="p-card"><strong>Environment</strong>
      <div class="meta" style="margin-top:4px;font-family:var(--font-editor);font-size:10px">${esc(State.app.runtimeDir || "")}</div>
    </div></div>`;
}
function wireAccountPanel() {
  const upload = () => $("#pick-avatar")?.click();
  $("#acct-avatar")?.addEventListener("click", upload);
  $("#acct-upload")?.addEventListener("click", upload);
  $("#acct-remove")?.addEventListener("click", async () => { await api("remove_profile_image"); State.profilePicture = null; renderExplorerBody(); });
}

function openScript(s) {
  const ex = State.tabs.find(t => (t.scriptId && t.scriptId === s.id) || (!t.scriptId && t.title === s.title));
  if (ex) return selectTab(ex.id);
  createTab(s.title, s.content, s.id);
}

// Tabs
function createTab(title, content, scriptId) {
  const rt = title || "Untitled";
  const ex = State.tabs.find(t => {
    if (scriptId && t.scriptId === scriptId) return true;
    if (!scriptId && t.title === rt && !t.scriptId) return true;
    return false;
  });
  if (ex) return selectTab(ex.id);
  const id = `tab_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
  const empty = State.settings?.general?.defaultNewTabBehavior === "empty";
  const body = content !== undefined ? content : (empty ? "" : "-- Untitled Script\n");
  const tab = { id, title: rt, content: body, saved: body, scriptId: scriptId || null, dirty: false };
  State.tabs.push(tab); selectTab(id);
}
function selectTab(id) {
  const t = State.tabs.find(x => x.id === id); if (!t) return;
  State.activeTab = id;
  $("#editor-input").value = t.content;
  $("#sb-path").textContent = t.title;
  renderTabs(); refreshEditor(true);
}
function renderTabs() {
  const bar = $("#tabs"); if (!bar) return;
  bar.innerHTML = "";
  State.tabs.forEach(t => {
    const el = document.createElement("div");
    el.className = `tab${t.id === State.activeTab ? " active" : ""}${t.dirty ? " dirty" : ""}`;
    el.dataset.id = t.id;
    el.innerHTML = `<span class="tab-quote">"</span><span class="tab-name">${esc(t.title)}</span><span class="tab-dirty"></span><button class="tab-close"><svg viewBox="0 0 12 12"><line x1="2.5" y1="2.5" x2="9.5" y2="9.5"/><line x1="9.5" y1="2.5" x2="2.5" y2="9.5"/></svg></button>`;
    el.addEventListener("click", () => selectTab(t.id));
    el.querySelector(".tab-close").addEventListener("click", (ev) => { ev.stopPropagation(); closeTab(t.id); });
    el.addEventListener("contextmenu", (ev) => {
      ev.preventDefault(); State.ctxTab = t.id;
      const m = $("#tab-ctx"); m.classList.add("open");
      m.style.left = Math.min(ev.clientX, innerWidth - 180) + "px";
      m.style.top = Math.min(ev.clientY, innerHeight - 180) + "px";
    });
    bar.appendChild(el);
  });
}
async function closeTab(id) {
  const idx = State.tabs.findIndex(x => x.id === id); if (idx === -1) return;
  const t = State.tabs[idx];
  if (t.dirty && State.settings?.editor?.confirmCloseUnsaved) {
    if (!await uiConfirm(`Close "${t.title}" with unsaved changes?`, "Close Tab", "Close", true)) return;
  }
  if (State.tabs.length === 1) { t.title = "Untitled"; t.content = ""; t.saved = ""; t.dirty = false; t.scriptId = null; $("#editor-input").value = ""; selectTab(t.id); return; }
  State.tabs.splice(idx, 1);
  if (State.activeTab === id) selectTab(State.tabs[Math.max(0, idx - 1)].id);
  else renderTabs();
}

// Editor
let lastGutter = 0;
function refreshEditor(force) {
  const inp = $("#editor-input"), syn = $("#syntax"), gut = $("#gutter");
  if (!inp) return;
  const val = inp.value, sel = inp.selectionStart || 0;
  let lines = 1, curLine = 1, lastNl = -1;
  for (let i = 0; i < val.length; i++) {
    if (val.charCodeAt(i) === 10) { lines++; if (i < sel) { curLine++; lastNl = i; } }
  }
  const col = sel - lastNl;
  syn.innerHTML = highlight(val);
  syn.scrollTop = inp.scrollTop; syn.scrollLeft = inp.scrollLeft;
  if (force || lines !== lastGutter) {
    lastGutter = lines;
    const frag = document.createDocumentFragment();
    for (let i = 1; i <= lines; i++) {
      const d = document.createElement("div"); d.className = `gln${i === curLine ? " active" : ""}`; d.textContent = i; frag.appendChild(d);
    }
    gut.innerHTML = ""; gut.appendChild(frag);
  }
  gut.scrollTop = inp.scrollTop;
  const fs = Number(State.settings?.editor?.fontSize || 13);
  const lh = Number(State.settings?.editor?.lineHeight || 1.55) * fs;
  $("#current-line").style.transform = `translate3d(0, ${10 + (curLine - 1) * lh - inp.scrollTop}px, 0)`;
  $("#sb-cursor").textContent = `Ln ${curLine}, Col ${col}`;
}

function logMessage(tab, text, level="info") {
  const ts = new Date().toTimeString().slice(0, 8);
  const b = State.logs[tab] || (State.logs[tab] = []);
  b.push({ts, text, level});
  const max = Number(State.settings?.console?.maxLines || 2000);
  if (b.length > max) b.shift();
  if (State.activeBottomTab === tab) renderLogs();
}
function renderLogs() {
  const box = $("#bottom-body"); if (!box) return;
  const list = State.logs[State.activeBottomTab] || [];
  box.innerHTML = ""; box.classList.toggle("empty", !list.length);
  if (!list.length) { box.textContent = "Terminal ready."; return; }
  const frag = document.createDocumentFragment();
  list.forEach(it => {
    const d = document.createElement("div"); d.className = `log-line ${it.level}`;
    d.innerHTML = `<span class="log-time">[${it.ts}]</span><span class="log-msg">${esc(it.text)}</span>`;
    frag.appendChild(d);
  });
  box.appendChild(frag);
  if (State.settings?.console?.autoScroll !== false) box.scrollTop = box.scrollHeight;
}
function setBottomTab(t) {
  State.activeBottomTab = t;
  $$(".btab").forEach(b => b.classList.toggle("active", b.dataset.btab === t));
  renderLogs();
}

function setAttached(attached, pid, version, method) {
  State.attached = !!attached;
  $("#sb-dot").classList.toggle("on", !!attached);
  $("#sb-inject-label").textContent = attached ? (pid ? `Attached · ${pid}` : "Attached") : "Not injected";
  $("#home-inject").textContent = attached ? "Injected" : "Not injected";
  $("#home-inject").className = "v " + (attached ? "ok" : "");
  $("#sb-version").textContent = version ? version.replace("version-", "v") : "—";
}

async function doAttach(targetPid) {
  const ov = $("#attach-overlay"), st = $("#attach-step");
  const steps = ["Checking DLL...", "Syncing offsets...", "Opening process...", "Injecting...", "Verifying..."];
  let i = 0; ov.classList.add("open"); st.textContent = steps[0];
  const iv = setInterval(() => { i = Math.min(i+1, steps.length-1); st.textContent = steps[i]; }, 350);
  try {
    const res = await api("simulate_attach", targetPid ? {pid: targetPid} : {});
    clearInterval(iv); ov.classList.remove("open");
    if (res?.ok) {
      setAttached(true, res.pid, res.clientVersion, "attach");
      logMessage("terminal", res.message, "ok");
      showToast(res.message, "ok");
    } else {
      logMessage("terminal", res?.error || "Attach failed", "err");
      showToast(res?.error || "Attach failed", "err");
    }
  } catch (e) {
    clearInterval(iv); ov.classList.remove("open");
    showToast("Attach failed: " + e, "err");
  }
}

async function doLaunchInject(version) {
  const ov = $("#attach-overlay"), st = $("#attach-step");
  const steps = ["Syncing offsets...", "Writing module config...", "Launching suspended...", "Early-bird inject...", "Resuming client..."];
  let i = 0; ov.classList.add("open"); st.textContent = steps[0];
  const iv = setInterval(() => { i = Math.min(i+1, steps.length-1); st.textContent = steps[i]; }, 500);
  try {
    const res = await api("launch_and_inject", { version: version || "" });
    clearInterval(iv); ov.classList.remove("open");
    if (res?.ok) {
      setAttached(true, res.pid, res.version || "", res.method);
      logMessage("terminal", res.message, "ok");
      showToast(res.message, "ok");
    } else {
      logMessage("terminal", res?.error || "Launch & Inject failed", "err");
      showToast(res?.error || "Launch & Inject failed", "err");
    }
  } catch (e) {
    clearInterval(iv); ov.classList.remove("open");
    showToast("Launch failed: " + e, "err");
  }
}

function switchView(name) {
  State.currentView = name;
  $$(".nav-icon[data-view]").forEach(b => b.classList.toggle("active", b.dataset.view === name));
  $$("#workspace > section").forEach(s => s.classList.remove("active"));
  $(`#view-${name}`)?.classList.add("active");
  if (name === "settings") renderSettingsNav();
}

// Settings
const SETTINGS_SECTIONS = [
  { id:"roblox", name:"Roblox", icon:THEME_ICONS.roblox },
  { id:"versions", name:"Versions", icon:THEME_ICONS.versions },
  { id:"appearance", name:"Appearance", icon:THEME_ICONS.appearance },
  { id:"effects", name:"Effects", icon:THEME_ICONS.effects },
  { id:"editor", name:"Editor", icon:THEME_ICONS.editor },
  { id:"terminal", name:"Terminal", icon:THEME_ICONS.terminal },
  { id:"window", name:"Window", icon:THEME_ICONS.window },
  { id:"behavior", name:"Behavior", icon:THEME_ICONS.behavior },
  { id:"connections", name:"Connections", icon:THEME_ICONS.connections },
  { id:"secret", name:"???", icon:THEME_ICONS.secret, secret:true },
];

function renderSettingsNav() {
  const nav = $("#settings-cats"); nav.innerHTML = "";
  SETTINGS_SECTIONS.forEach(s => {
    const b = document.createElement("button");
    b.className = `s-cat${State.settingsSection === s.id ? " active" : ""}${s.secret ? " s-cat-secret" : ""}`;
    b.innerHTML = `<svg viewBox="0 0 24 24">${s.icon}</svg><span class="s-cat-name">${esc(s.name)}</span>`;
    b.addEventListener("click", () => { State.settingsSection = s.id; renderSettingsNav(); });
    nav.appendChild(b);
  });
  renderSettingsBody();
}
const swEl = (bind, on) => `<div class="sw${on ? " on" : ""}" data-bind="${bind}"></div>`;
const row = (t, d, c) => `<div class="s-row"><div class="s-row-info"><div class="s-row-title">${esc(t)}</div><div class="s-row-desc">${esc(d)}</div></div><div class="s-row-control">${c}</div></div>`;
const sliderEl = (id, mn, mx, v, sfx="", st=1) => `<div class="slider-wrap"><input type="range" class="slider" id="${id}" min="${mn}" max="${mx}" step="${st}" value="${v}" /><span class="slider-val" id="${id}-lbl">${v}${sfx}</span></div>`;
const selectEl = (bind, opts, v) => `<select class="ui-select" data-select="${bind}">${opts.map(o => `<option value="${o.v}"${String(v)===String(o.v)?" selected":""}>${o.l}</option>`).join("")}</select>`;
const segEl = (id, opts, v) => `<div class="segmented" id="${id}">${opts.map(o => `<button data-v="${o.v}"${String(v)===String(o.v)?' class="active"':""}>${o.l}</button>`).join("")}</div>`;

function buildSectionHtml(secId) {
  const s = State.settings; if (!s) return "";
  let h = "";
  if (secId === "roblox") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Roblox</div><div class="s-section-sub">Attach, injection methods, and module features.</div></div></div>`;
    h += row("Module.dll", "Auto-detected next to kitty.py or in ./bin/",
      `<span class="s-row-desc mono" style="font-family:var(--font-editor);font-size:10px;word-break:break-all" id="cfg-dll-path">${esc(State.offsets?.dll_path || "not found")}</span>`);
    h += row("Offsets version", "Auto-fetched from offsets.imtheo.lol.",
      `<span class="s-row-desc mono" style="font-family:var(--font-editor);font-size:10px" id="cfg-offsets-version">${esc(State.offsets?.cached_version || "not cached")}</span>`);
    h += row("Sync offsets now", "Force-refresh the offsets table.", `<button class="btn primary" id="cfg-sync-offsets">Sync</button>`);
    h += `<div class="s-subhead">Injection methods</div>`;
    h += row("Prefer suspended injection", "Launch Roblox suspended, inject before its own checks run, then resume.", swEl("roblox.preferSuspendedInject", s.roblox.preferSuspendedInject !== false));
    h += row("Force old-version bypass", "Try extra strategies when the target is an older client.", swEl("roblox.forceOldVersionBypass", s.roblox.forceOldVersionBypass !== false));
    h += row("Patch ClientVersion in memory", "Rewrite the client's own version string to the newest installed one.", swEl("roblox.patchClientVersion", s.roblox.patchClientVersion !== false));
    h += row("Skip version check", "Tells the module to skip its own version check.", swEl("roblox.skipVersionCheck", s.roblox.skipVersionCheck !== false));
    h += row("Prefer NtCreateThreadEx", "Use NTCT instead of CreateRemoteThread for the running-client path.", swEl("roblox.useManualMapper", !!s.roblox.useManualMapper));
    h += row("Inject timeout", "Seconds to wait for Roblox to spin up before injecting.", sliderEl("set-inject-timeout", 5, 180, s.roblox.injectTimeoutSec ?? 60, "s"));
    h += `<div class="s-subhead">Executor features</div>`;
    h += row("RakNet", "Enable RakNet library in the module.", swEl("roblox.raknet", s.roblox.raknet));
    h += row("Internal UI", "Enable the module's internal UI panel.", swEl("roblox.internalUI", s.roblox.internalUI));
    h += row("Bypass AFK", "Keep the client from idling out.", swEl("roblox.bypassAFK", s.roblox.bypassAFK !== false));
    h += row("AutoExec", "Run AutoExec scripts when injection completes.", swEl("roblox.autoAttach", s.roblox.autoAttach));
    h += `<div class="s-subhead">Execution socket</div>`;
    h += row("Exec host", "Socket host the module listens on.", `<input type="text" class="ui-text mono" data-text="roblox.execHost" value="${esc(s.roblox.execHost)}" />`);
    h += row("Exec port", "Socket port the module listens on.", `<input type="text" class="ui-text mono" data-text="roblox.execPort" value="${esc(s.roblox.execPort)}" />`);
    h += row("Actions", "Status and process management.", `<button class="btn" id="cfg-status">Check</button> <button class="btn danger" id="cfg-kill">Kill Roblox</button>`);
  } else if (secId === "versions") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Versions</div><div class="s-section-sub">Launch a specific installed client and inject into it. Works with old versions via suspended injection.</div></div></div>`;
    h += `<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Installed Roblox Versions</div><div class="s-row-desc">Detected in <code>%LOCALAPPDATA%\\Roblox\\Versions</code>. Sorted newest first.</div></div>
      <div class="version-list" id="versions-list">
        ${(State.versions || []).map((v, i) => `
          <div class="version-row${State.selectedVersion === v.name ? " active" : ""}" data-version="${esc(v.name)}">
            <div class="vinfo">
              <div class="vname">${esc(v.name)}</div>
              <div class="vmeta">${new Date((v.modified || 0) * 1000).toLocaleString()}${i === 0 ? " · NEWEST" : ""}</div>
            </div>
            <button class="btn primary" data-launch="${esc(v.name)}">Launch &amp; Inject</button>
          </div>`).join("") || `<div class="p-card"><strong>No versions found</strong><div class="meta">Make sure Roblox is installed and has been launched at least once.</div></div>`}
      </div>
    </div>`;
    h += row("Refresh list", "Rescan installed Roblox versions.", `<button class="btn" id="cfg-refresh-versions">Refresh</button>`);
  } else if (secId === "appearance") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Appearance</div><div class="s-section-sub">Theme, background, border, ambient FX.</div></div></div>`;
    h += `<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Theme</div></div><div class="theme-grid" id="theme-grid"></div></div>`;
    h += `<div class="s-subhead">Border</div>`;
    h += row("Enable border", "Colored border around the window.", swEl("appearance.borderEnabled", s.appearance.borderEnabled !== false));
    h += row("Border mode", "Rainbow or solid.", segEl("seg-border-mode", [{v:"rainbow",l:"Rainbow"},{v:"solid",l:"Solid"},{v:"off",l:"Off"}], s.appearance.borderMode));
    if (s.appearance.borderMode === "solid") h += row("Border color", "Solid color.", `<input type="color" class="mini-color" id="border-color" value="${s.appearance.borderColor}" />`);
    h += row("Border width", "Thickness.", sliderEl("set-border-width", 1, 8, s.appearance.borderWidth || 2, "px"));
    h += `<div class="s-subhead">Background image</div>`;
    h += `<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Wallpaper</div></div><div class="bg-thumbs" id="bg-thumbs"></div>
      <div style="display:flex;gap:6px;margin-top:10px"><button class="btn primary" id="cfg-upload-apply">Upload &amp; Apply</button><button class="btn danger" id="cfg-remove-bg">Remove</button></div></div>`;
    h += row("Opacity", "Wallpaper visibility.", sliderEl("set-bg-strength", 0, 100, s.appearance.bgImageOpacity, "%"));
    h += row("Blur", "Blur radius.", sliderEl("set-bg-blur", 0, 32, s.appearance.bgImageBlur, "px"));
    h += row("Saturation", "Colour intensity.", sliderEl("set-bg-sat", 0, 200, s.appearance.bgImageSaturation, "%"));
    h += row("Panel opacity", "Panel transparency over the wallpaper.", sliderEl("set-panel-opacity", 30, 100, s.appearance.panelOpacity, "%"));
    h += row("Image-derived colors", "Use the wallpaper to recolor the UI.", swEl("appearance.imageAutoTheme", s.appearance.imageAutoTheme !== false));
    h += `<div class="s-subhead">Ambient FX</div>`;
    h += row("Effect", "Background particles.", segEl("seg-fx-type", [{v:"off",l:"Off"},{v:"orbs",l:"Orbs"},{v:"sparkles",l:"Sparkles"},{v:"aurora",l:"Aurora"}], s.appearance.fxType));
    h += row("Intensity", "Density.", segEl("seg-fx-int", [{v:"low",l:"Low"},{v:"med",l:"Med"},{v:"high",l:"High"}], s.appearance.fxIntensity));
    h += row("FX opacity", "Overall visibility.", segEl("seg-fx-op", [{v:"dim",l:"Dim"},{v:"normal",l:"Normal"},{v:"bold",l:"Bold"}], s.appearance.fxOpacity));
    h += `<div class="s-subhead">Surface</div>`;
    h += row("Accent override", "Custom accent color (hex).", `<input type="color" class="mini-color" id="cfg-accent" value="${s.appearance.customAccentHex || '#1e3a5f'}" /><input type="text" class="ui-text mono" data-text="appearance.customAccentHex" value="${esc(s.appearance.customAccentHex || '')}" style="width:100px" />`);
    h += row("Density", "Compact, comfortable, spacious.", selectEl("appearance.uiDensity", [{v:"compact",l:"Compact"},{v:"comfortable",l:"Comfortable"},{v:"spacious",l:"Spacious"}], s.appearance.uiDensity));
    h += row("Corner radius", "Sharp, subtle, rounded.", selectEl("appearance.cornerRadius", [{v:"sharp",l:"Sharp"},{v:"subtle",l:"Subtle"},{v:"rounded",l:"Rounded"}], s.appearance.cornerRadius));
    h += row("Sidebar labels", "Show filenames.", swEl("appearance.sidebarLabels", s.appearance.sidebarLabels !== false));
    h += row("Sidebar icon size", "Icon size.", sliderEl("set-sidebar-icon", 10, 22, s.appearance.sidebarIconSize, "px"));
  } else if (secId === "effects") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Effects</div><div class="s-section-sub">Particles, cursor, motion.</div></div></div>`;
    h += row("Click particles", "Burst on click.", swEl("effects.clickParticles", s.effects.clickParticles));
    h += row("Particle count", "Particles per click.", sliderEl("set-particle-count", 4, 36, s.effects.particleCount ?? 16, ""));
    h += row("Particle color", "Leave default to use accent.", `<input type="color" class="mini-color" id="particle-color" value="${s.effects.particleColor || '#1e3a5f'}" />`);
    h += row("Cursor trail", "Trail dots following the pointer.", swEl("effects.cursorTrail", s.effects.cursorTrail));
    h += row("Trail interval", "Lower = denser trail.", sliderEl("set-trail-rate", 12, 100, s.effects.trailIntervalMs ?? 42, "ms"));
    h += row("Water cursor", "Glassy rings following cursor.", swEl("effects.waterCursor", s.effects.waterCursor !== false));
    h += row("Water intensity", "Ring strength.", sliderEl("set-water-intensity", 1, 10, s.effects.waterIntensity ?? 5, "/10"));
    h += row("Water size", "Max ring radius.", sliderEl("set-water-size", 24, 150, s.effects.waterSize ?? 76, "px"));
    h += row("Ripples", "Button click ripples.", swEl("effects.ripplesEnabled", s.effects.ripplesEnabled));
    h += row("Fog glow", "Hover breathing glow.", swEl("effects.fogGlow", s.effects.fogGlow !== false));
    h += row("Master animations", "Enable all transitions.", swEl("effects.masterAnimations", s.effects.masterAnimations));
    h += row("Animation speed", "Duration preset.", selectEl("effects.animationSpeed", [{v:"slow",l:"Slow"},{v:"normal",l:"Normal"},{v:"fast",l:"Fast"}], s.effects.animationSpeed));
    h += row("Cursor spotlight", "Radial glow following pointer.", swEl("effects.cursorSpotlight", s.effects.cursorSpotlight));
    h += row("Reduced motion", "Disable nonessential animation.", swEl("effects.reduceMotion", s.effects.reduceMotion));
  } else if (secId === "editor") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Editor</div></div></div>`;
    h += row("Font family", "Monospace stack.", selectEl("editor.fontFamily", [{v:"Cascadia Code",l:"Cascadia Code"},{v:"JetBrains Mono",l:"JetBrains Mono"},{v:"Consolas",l:"Consolas"}], s.editor.fontFamily));
    h += row("Font size", "Scale in pixels.", sliderEl("set-font-size", 11, 20, s.editor.fontSize, "px"));
    h += row("Line height", "Vertical rhythm.", sliderEl("set-line-height", 1.2, 2.0, s.editor.lineHeight, "", 0.05));
    h += row("Line numbers", "Gutter numbers.", swEl("editor.lineNumbers", s.editor.lineNumbers));
    h += row("Current line", "Highlight cursor line.", swEl("editor.highlightCurrentLine", s.editor.highlightCurrentLine));
    h += row("Word wrap", "Wrap long lines.", swEl("editor.wordWrap", s.editor.wordWrap));
    h += row("Tab size", "Indentation width.", selectEl("editor.tabSize", [{v:2,l:"2"},{v:4,l:"4"},{v:8,l:"8"}], s.editor.tabSize));
    h += row("Auto indent", "Indent on Enter.", swEl("editor.autoIndent", s.editor.autoIndent));
    h += row("Auto-close brackets", "Auto-pair brackets and quotes.", swEl("editor.autoCloseBrackets", s.editor.autoCloseBrackets));
  } else if (secId === "terminal") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Terminal</div></div></div>`;
    h += row("Show terminal", "Display bottom panel.", swEl("console.showConsole", s.console.showConsole));
    h += row("Height", "Panel height.", sliderEl("set-term-height", 100, 400, s.console.consoleHeight, "px"));
    h += row("Auto scroll", "Scroll to newest output.", swEl("console.autoScroll", s.console.autoScroll));
    h += row("Timestamps", "Prefix each line.", swEl("console.timestamps", s.console.timestamps));
    h += row("Max lines", "Retained lines.", selectEl("console.maxLines", [{v:500,l:"500"},{v:2000,l:"2,000"},{v:5000,l:"5,000"}], s.console.maxLines));
    h += row("Confirm clear", "Prompt before wiping output.", swEl("console.confirmClearOutput", s.console.confirmClearOutput));
  } else if (secId === "window") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Window</div></div></div>`;
    h += row("Launch maximized", "Open maximized.", swEl("general.launchMaximized", s.general.launchMaximized));
    h += row("Minimize to tray", "Hide to tray on close.", swEl("general.minimizeToTray", s.general.minimizeToTray));
    h += row("Streamproof (WDA)", "Exclude from OBS capture.", swEl("general.streamproof", s.general.streamproof));
    h += row("Disguise title", 'Rename window to "Spotify".', swEl("general.disguiseMode", s.general.disguiseMode));
    h += row("Global toggle key", "Hide/restore hotkey.", selectEl("general.globalToggleKey", [{v:"Insert",l:"Insert"},{v:"F8",l:"F8"},{v:"F9",l:"F9"},{v:"F10",l:"F10"},{v:"Home",l:"Home"}], s.general.globalToggleKey));
  } else if (secId === "behavior") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Behavior</div></div></div>`;
    h += row("Performance mode", "OS scheduling priority.", selectEl("general.performanceMode", [{v:"low",l:"Low"},{v:"medium",l:"Medium"},{v:"high",l:"High"}], s.general.performanceMode));
    h += row("Hover effects", "Lift and border on hover.", swEl("effects.hoverEffects", s.effects.hoverEffects));
    h += row("Magnetic icons", "Nav icons follow cursor.", swEl("effects.magneticIcons", s.effects.magneticIcons));
    h += row("Button press", "Scale feedback on click.", swEl("effects.buttonPressAnim", s.effects.buttonPressAnim));
    h += row("Glow effects", "Colored glow shadows.", swEl("effects.glowEffects", s.effects.glowEffects));
    h += row("Smooth scroll", "Smooth scrolling.", swEl("effects.smoothScrolling", s.effects.smoothScrolling !== false));
  } else if (secId === "connections") {
    h += `<div class="s-section-head"><div><div class="s-section-title">Connections</div></div></div>`;
    h += row("Runtime directory", "Where kitty.py lives.", `<span class="s-row-desc mono" style="font-family:var(--font-editor);font-size:10px;word-break:break-all">${esc(State.app.runtimeDir || "")}</span>`);
    h += row("Settings file", "Persisted config.", `<span class="s-row-desc mono" style="font-family:var(--font-editor);font-size:10px;word-break:break-all">${esc(State.app.settingsPath || "")}</span>`);
    h += row("Export settings", "Save to JSON.", `<button class="btn" id="cfg-export">Export</button>`);
    h += row("Import settings", "Load from JSON.", `<button class="btn" id="cfg-import">Import</button>`);
    h += row("Open data folder", "Open Kitty data directory.", `<button class="btn" id="cfg-folder">Open</button>`);
    h += row("Reset all settings", "Restore defaults.", `<button class="btn danger" id="cfg-reset">Reset</button>`);
  } else if (secId === "secret") {
    const un = s.secret?.unlocked;
    h += `<div class="s-section-head"><div><div class="s-section-title">${un ? "The Void" : "???"}</div><div class="s-section-sub">${un ? "Unlocked." : "Something is hidden here."}</div></div></div>`;
    if (!un) {
      h += `<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Seal of the Void</div><div class="s-row-desc">Click colors in ROYGBP order.</div></div>
        <div style="display:flex;gap:14px;justify-content:center;padding:20px;background:var(--bg);border:1px dashed var(--border-strong);border-radius:6px;margin-top:8px" id="seal-wrap">
          ${["#3498db","#e74c3c","#9b59b6","#f1c40f","#2ecc71","#f39c12"].map(c => `<div class="seal-dot" data-color="${c}" style="width:44px;height:44px;border-radius:50%;background:${c};cursor:pointer"></div>`).join("")}
        </div></div>`;
    } else {
      h += row("Reaper mode", "Swap brand identity for the grim reaper.", swEl("secret.reaperMode", s.secret.reaperMode));
      h += row("Re-lock", "Reset the seal.", `<button class="btn" id="reaper-relock">Re-lock</button>`);
    }
  }
  return h;
}

function renderSettingsBody() {
  const body = $("#settings-body");
  if (!body || !State.settings) return;
  body.innerHTML = buildSectionHtml(State.settingsSection);
  wireSettingsControls();
  if (State.settingsSection === "appearance") { renderThemeGrid(); renderBackgroundThumbs(); }
  if (State.settingsSection === "secret") wireSealPanel();
}

function syncSettingsInputs() {
  $$(".sw[data-bind]").forEach(el => {
    const [s, k] = el.dataset.bind.split(".");
    el.classList.toggle("on", !!State.settings[s]?.[k]);
  });
  $$(".ui-select[data-select]").forEach(el => {
    const [s, k] = el.dataset.select.split(".");
    const v = State.settings[s]?.[k];
    if (v !== undefined) el.value = String(v);
  });
}

function wireSettingsControls() {
  $$(".sw[data-bind]").forEach(el => el.addEventListener("click", () => {
    const [s, k] = el.dataset.bind.split(".");
    const next = !State.settings[s]?.[k];
    patchSettings({ [s]: { [k]: next } });
  }));
  $$(".ui-select[data-select]").forEach(el => el.addEventListener("change", () => {
    const [s, k] = el.dataset.select.split(".");
    const raw = el.value;
    const val = /^\d+$/.test(raw) ? Number(raw) : raw;
    patchSettings({ [s]: { [k]: val } });
  }));
  $$(".ui-text[data-text]").forEach(el => el.addEventListener("change", () => {
    const [s, k] = el.dataset.text.split(".");
    let v = el.value.trim();
    if (/^-?\d+$/.test(v)) v = Number(v);
    patchSettings({ [s]: { [k]: v } });
  }));
  const segMap = {
    "seg-border-mode":"appearance.borderMode",
    "seg-fx-type":"appearance.fxType",
    "seg-fx-int":"appearance.fxIntensity",
    "seg-fx-op":"appearance.fxOpacity",
  };
  $$(".segmented").forEach(seg => {
    const bind = segMap[seg.id]; if (!bind) return;
    seg.addEventListener("click", (ev) => {
      const b = ev.target.closest("button"); if (!b) return;
      const [s, k] = bind.split(".");
      patchSettings({ [s]: { [k]: b.dataset.v } });
    });
  });
  const sliders = [
    ["set-inject-timeout", v => ({ roblox: { injectTimeoutSec: v } }), "s"],
    ["set-panel-opacity", v => ({ appearance: { panelOpacity: v } }), "%"],
    ["set-bg-strength", v => ({ appearance: { bgImageOpacity: v } }), "%"],
    ["set-bg-blur", v => ({ appearance: { bgImageBlur: v } }), "px"],
    ["set-bg-sat", v => ({ appearance: { bgImageSaturation: v } }), "%"],
    ["set-font-size", v => ({ editor: { fontSize: v } }), "px"],
    ["set-line-height", v => ({ editor: { lineHeight: v } }), ""],
    ["set-term-height", v => ({ console: { consoleHeight: v } }), "px"],
    ["set-sidebar-icon", v => ({ appearance: { sidebarIconSize: v } }), "px"],
    ["set-particle-count", v => ({ effects: { particleCount: v } }), ""],
    ["set-trail-rate", v => ({ effects: { trailIntervalMs: v } }), "ms"],
    ["set-water-intensity", v => ({ effects: { waterIntensity: v } }), "/10"],
    ["set-water-size", v => ({ effects: { waterSize: v } }), "px"],
    ["set-border-width", v => ({ appearance: { borderWidth: v } }), "px"],
  ];
  sliders.forEach(([id, map, sfx]) => {
    const el = $(`#${id}`); const lbl = $(`#${id}-lbl`); if (!el) return;
    el.addEventListener("input", () => {
      const v = Number(el.value); if (lbl) lbl.textContent = v + sfx;
      patchSettings(map(v));
    });
  });
  $("#cfg-sync-offsets")?.addEventListener("click", async (ev) => {
    const b = ev.currentTarget; b.disabled = true; b.textContent = "...";
    const r = await api("sync_offsets", { force: true });
    if (r?.ok) { showToast(`Offsets synced: ${r.version || "unknown"}`, "ok"); logMessage("terminal", `Offsets synced: ${r.version}`, "ok"); }
    else { showToast(r?.error || "Sync failed", "err"); }
    State.offsets = await api("offsets_status");
    renderSettingsBody();
  });
  $("#cfg-status")?.addEventListener("click", async () => {
    const r = await api("get_status");
    if (r) { setAttached(!!r.attached, r.attached_pid, r.attached_version, r.attached_method); logMessage("roblox", r.attached ? `Attached (PID ${r.attached_pid}, ${r.attached_version})` : "Not attached", r.attached ? "ok" : "warn"); }
  });
  $("#cfg-kill")?.addEventListener("click", async () => {
    if (!await uiConfirm("Terminate all Roblox processes?", "Kill Roblox", "Kill", true)) return;
    const r = await api("kill_roblox");
    if (r?.ok) { logMessage("terminal", `Killed ${r.killed}`, "warn"); setAttached(false); }
  });
  $("#cfg-refresh-versions")?.addEventListener("click", async () => {
    const init = await api("get_initial_state");
    if (init?.ok) { State.versions = init.installedVersions || []; renderSettingsBody(); }
  });
  $$("[data-launch]").forEach(btn => btn.addEventListener("click", () => {
    const v = btn.dataset.launch;
    State.selectedVersion = v;
    doLaunchInject(v);
  }));
  $("#cfg-upload-apply")?.addEventListener("click", async () => {
    const r = await api("pick_theme_image");
    if (r?.ok) { State.pendingDataUrl = r.dataUrl; State.pendingFilename = r.filename; State.pendingPalette = r.pilPalette; }
    else if (r?.fallback) $("#pick-image").click();
    else return;
    if (State.pendingDataUrl) {
      const saved = await api("save_custom_theme_image", { filename: State.pendingFilename, dataUrl: State.pendingDataUrl, palette: State.pendingPalette });
      if (saved?.ok) { State.settings = saved.settings; await patchSettings({ appearance: { useBackgroundImage: true } }); renderSettingsBody(); showToast("Background applied", "ok"); }
    }
  });
  $("#cfg-remove-bg")?.addEventListener("click", async () => {
    const r = await api("remove_custom_theme_image");
    if (r?.ok) { State.settings = r.settings; applySettings(); renderSettingsBody(); }
  });
  $("#cfg-accent")?.addEventListener("change", (e) => patchSettings({ appearance: { customAccentHex: e.target.value } }));
  $("#border-color")?.addEventListener("change", (e) => patchSettings({ appearance: { borderColor: e.target.value } }));
  $("#particle-color")?.addEventListener("change", (e) => patchSettings({ effects: { particleColor: e.target.value } }));
  $("#cfg-export")?.addEventListener("click", async () => {
    const r = await api("export_settings_json");
    if (r?.browserDownload && r.json) {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([r.json], { type:"application/json" }));
      a.download = "kitty_settings.json"; a.click();
    }
  });
  $("#cfg-import")?.addEventListener("click", async () => {
    if (window.pywebview) { const r = await api("import_settings_json", {}); if (r?.ok) { State.settings = r.settings; applySettings(); } }
    else $("#pick-json").click();
  });
  $("#cfg-folder")?.addEventListener("click", () => api("open_data_folder"));
  $("#cfg-reset")?.addEventListener("click", async () => {
    if (!await uiConfirm("Reset all settings?", "Reset", "Reset", true)) return;
    const r = await api("reset_all_settings");
    if (r?.ok) { State.settings = r.settings; applySettings(); renderSettingsBody(); }
  });
  $("#reaper-relock")?.addEventListener("click", () => patchSettings({ secret: { unlocked: false, reaperMode: false } }));
}

function wireSealPanel() {
  if (State.settings?.secret?.unlocked) return;
  const order = ["#e74c3c","#f39c12","#f1c40f","#2ecc71","#3498db","#9b59b6"];
  let progress = [];
  $$("#seal-wrap .seal-dot").forEach(d => d.addEventListener("click", () => {
    const c = d.dataset.color;
    if (c === order[progress.length]) {
      progress.push(c);
      d.style.boxShadow = "0 0 20px 4px #fff";
      if (progress.length === order.length) {
        setTimeout(() => patchSettings({ secret: { unlocked: true } }), 300);
        showToast("The seal is broken.", "warn");
      }
    } else {
      progress = [];
      $$("#seal-wrap .seal-dot").forEach(x => x.style.boxShadow = "none");
    }
  }));
}

function renderThemeGrid() {
  const g = $("#theme-grid"); if (!g || !State.settings?.appearance) return;
  const a = State.settings.appearance;
  g.innerHTML = "";
  const hidden = new Set(["reaper","void-green","void-mono"]);
  Object.values(State.builtinThemes).forEach(t => {
    if (hidden.has(t.id) && !State.settings.secret?.unlocked) return;
    if (t.id === "reaper") return;
    const active = a.theme === t.id;
    const c = document.createElement("div");
    c.className = `theme-card${active ? " active" : ""}`;
    c.innerHTML = `<div class="theme-card-head"><span class="theme-card-name">${esc(t.name)}</span><span class="theme-check">${active ? "✓ ACTIVE" : "SELECT"}</span></div><div class="theme-dots"><span class="theme-dot" style="background:${t.bg}"></span><span class="theme-dot" style="background:${t.panel}"></span><span class="theme-dot" style="background:${t.accent}"></span></div><div class="theme-card-desc">${esc(t.desc)}</div>`;
    c.addEventListener("click", () => patchSettings({ appearance: { theme: t.id, customAccentHex: "" } }));
    g.appendChild(c);
  });
}
function renderBackgroundThumbs() {
  const box = $("#bg-thumbs"); if (!box) return;
  box.innerHTML = "";
  const ct = State.settings.appearance.customTheme || {};
  if (ct.imageDataUrl) {
    const img = document.createElement("div"); img.className = "bg-thumb active";
    img.innerHTML = `<img src="${ct.imageDataUrl}" alt="" />`;
    box.appendChild(img);
  } else {
    box.innerHTML = `<div class="bg-thumb"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>`;
  }
}

// Command palette
const COMMANDS = [
  { label:"Execute script", kb:"Ctrl+Enter", run:() => $("#rail-execute").click() },
  { label:"Attach (running Roblox)", run:() => doAttach() },
  { label:"Launch & Inject (newest)", run:() => doLaunchInject("") },
  { label:"New tab", kb:"Ctrl+N", run:() => createTab() },
  { label:"Save", kb:"Ctrl+S", run:() => $("#tb-save").click() },
  { label:"Open file", run:() => $("#tb-open").click() },
  { label:"Toggle terminal", kb:"Ctrl+J", run:() => patchSettings({ console: { showConsole: !State.settings.console.showConsole } }) },
  { label:"Toggle sidebar", kb:"Ctrl+B", run:() => handleActivityClick(State.lastActivity) },
  { label:"Settings", run:() => switchView("settings") },
  { label:"Home", run:() => switchView("home") },
];
function openCmd() {
  $("#cmd-back").classList.add("open");
  $("#cmd-input").value = ""; $("#cmd-input").focus();
  renderCmdList("");
}
function renderCmdList(q) {
  const list = $("#cmd-list"); list.innerHTML = "";
  const c = q.trim().toLowerCase();
  COMMANDS.filter(x => !c || x.label.toLowerCase().includes(c)).forEach((cmd, i) => {
    const r = document.createElement("div");
    r.className = `cmd-row${i === 0 ? " selected" : ""}`;
    r.innerHTML = `<span>${esc(cmd.label)}</span><span class="cmd-kb">${esc(cmd.kb || "")}</span>`;
    r.addEventListener("click", () => { $("#cmd-back").classList.remove("open"); cmd.run(); });
    list.appendChild(r);
  });
}

// Wire everything
function wireAll() {
  $("#win-min").addEventListener("click", () => api("window_minimize"));
  $("#win-max").addEventListener("click", () => api("window_maximize"));
  $("#win-close").addEventListener("click", () => api("window_close"));
  $$(".nav-icon[data-view]").forEach(b => b.addEventListener("click", () => switchView(b.dataset.view)));
  $("#nav-cmd").addEventListener("click", openCmd);
  $("#nav-clients").addEventListener("click", showClients);
  $$(".act-btn").forEach(b => b.addEventListener("click", () => handleActivityClick(b.dataset.act)));
  $("#explorer-collapse").addEventListener("click", () => { State.explorerVisible = false; syncExplorerVisibility(); patchSettings({ console: { leftExplorerVisible: false } }); });

  $("#tab-new").addEventListener("click", () => createTab());
  $("#tb-open").addEventListener("click", async () => {
    const r = await api("open_script_file");
    if (r?.ok) createTab(r.filename, r.content);
    else if (r?.fallback) $("#pick-script").click();
  });
  $("#tb-save").addEventListener("click", saveActive);
  $("#tb-find").addEventListener("click", () => openFind(false));
  $("#tb-replace").addEventListener("click", () => openFind(true));
  $("#tb-copy").addEventListener("click", async () => { try { await navigator.clipboard.writeText($("#editor-input").value); showToast("Copied", "ok"); } catch {} });
  $("#rail-save").addEventListener("click", saveActive);
  $("#rail-open").addEventListener("click", () => $("#tb-open").click());
  $("#rail-execute").addEventListener("click", executeActive);
  $("#rail-clear").addEventListener("click", () => { const i = $("#editor-input"); i.value = ""; i.dispatchEvent(new Event("input")); });
  $("#rail-launch").addEventListener("click", () => doLaunchInject(""));
  $("#rail-inject").addEventListener("click", () => doAttach());

  async function saveActive() {
    const t = State.tabs.find(x => x.id === State.activeTab); if (!t) return;
    const r = await api("save_script_file", { filename: t.title, content: $("#editor-input").value, direct: true });
    if (r?.ok) {
      t.saved = $("#editor-input").value; t.dirty = false; renderTabs();
      logMessage("terminal", `Saved "${t.title}"`, "ok"); showToast(`Saved ${t.title}`, "ok");
    }
  }
  async function executeActive() {
    const t = State.tabs.find(x => x.id === State.activeTab);
    const r = await api("simulate_execute", { title: t?.title || "Untitled", code: $("#editor-input").value });
    if (!r?.ok) { logMessage("terminal", r?.error || "Execute failed", "err"); showToast(r?.error || "Execute failed", "err"); return; }
    logMessage("terminal", `Executed "${r.title}" (${r.lines} lines)`, "ok");
    showToast(`Executed ${r.title}`, "ok");
  }

  const inp = $("#editor-input");
  inp.addEventListener("input", () => {
    const t = State.tabs.find(x => x.id === State.activeTab);
    if (t) {
      t.content = inp.value;
      const d = t.content !== t.saved;
      if (d !== t.dirty) { t.dirty = d; renderTabs(); }
    }
    refreshEditor(false);
  });
  inp.addEventListener("scroll", () => refreshEditor(false));
  inp.addEventListener("keyup", () => refreshEditor(false));
  inp.addEventListener("keydown", (ev) => {
    const ed = State.settings.editor;
    if (ev.key === "Tab") {
      ev.preventDefault();
      const ind = " ".repeat(Number(ed.tabSize || 4));
      inp.setRangeText(ind, inp.selectionStart, inp.selectionEnd, "end");
      inp.dispatchEvent(new Event("input"));
    } else if (ev.key === "Enter" && ed.autoIndent !== false) {
      const start = inp.selectionStart;
      const before = inp.value.slice(0, start);
      const cur = before.split("\n").pop() || "";
      const ind = (cur.match(/^\s*/) || [""])[0];
      const extra = /\b(then|do|function|repeat)\s*$/.test(cur.trim()) ? " ".repeat(Number(ed.tabSize||4)) : "";
      ev.preventDefault();
      inp.setRangeText("\n" + ind + extra, start, inp.selectionEnd, "end");
      inp.dispatchEvent(new Event("input"));
    } else if (ed.autoCloseBrackets !== false && inp.selectionStart === inp.selectionEnd) {
      const pairs = { "(":")", "[":"]", "{":"}", '"':'"', "'":"'" };
      if (pairs[ev.key]) {
        ev.preventDefault();
        const p = inp.selectionStart;
        inp.setRangeText(ev.key + pairs[ev.key], p, p, "end");
        inp.selectionStart = inp.selectionEnd = p + 1;
        inp.dispatchEvent(new Event("input"));
      }
    }
  });

  $$(".btab").forEach(b => b.addEventListener("click", () => setBottomTab(b.dataset.btab)));
  $("#term-copy").addEventListener("click", async () => {
    const txt = (State.logs[State.activeBottomTab] || []).map(l => `[${l.ts}] ${l.text}`).join("\n");
    try { await navigator.clipboard.writeText(txt); showToast("Copied", "ok"); } catch {}
  });
  $("#term-clear").addEventListener("click", () => { State.logs[State.activeBottomTab] = []; renderLogs(); });

  // Resizer
  const rsz = $("#bottom-resizer");
  rsz.addEventListener("pointerdown", (ev) => {
    ev.preventDefault();
    const startY = ev.clientY;
    const panel = $("#bottom-panel");
    const startH = panel.getBoundingClientRect().height;
    const move = (m) => { panel.style.height = Math.max(80, Math.min(500, startH - (m.clientY - startY))) + "px"; };
    const up = () => {
      window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up);
      patchSettings({ console: { consoleHeight: Math.round(panel.getBoundingClientRect().height) } });
    };
    window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
  });

  $("#inject-trigger").addEventListener("click", () => $("#inject-menu").classList.toggle("open"));
  document.addEventListener("click", (ev) => {
    if (!ev.target.closest("#inject-menu") && !ev.target.closest("#inject-trigger")) $("#inject-menu").classList.remove("open");
    $("#tab-ctx").classList.remove("open");
    if (!ev.target.closest("#file-ctx") && !ev.target.closest(".tree-item")) $("#file-ctx").classList.remove("open");
  });
  $("#menu-inject").addEventListener("click", () => { $("#inject-menu").classList.remove("open"); doAttach(); });
  $("#menu-launch-inject").addEventListener("click", () => { $("#inject-menu").classList.remove("open"); doLaunchInject(""); });
  $("#menu-clients").addEventListener("click", () => { $("#inject-menu").classList.remove("open"); showClients(); });
  $("#menu-kill").addEventListener("click", async () => {
    $("#inject-menu").classList.remove("open");
    if (!await uiConfirm("Terminate all Roblox processes?", "Kill", "Kill", true)) return;
    const r = await api("kill_roblox");
    if (r?.ok) { logMessage("terminal", `Killed ${r.killed}`, "warn"); setAttached(false); }
  });

  $("#find-close").addEventListener("click", () => $("#find-bar").classList.remove("open"));
  $("#find-next").addEventListener("click", () => {
    const n = $("#find-input").value; if (!n) return;
    const start = inp.selectionEnd;
    let idx = inp.value.indexOf(n, start);
    if (idx === -1) idx = inp.value.indexOf(n, 0);
    if (idx !== -1) { inp.focus(); inp.setSelectionRange(idx, idx + n.length); }
  });
  $("#replace-one").addEventListener("click", () => {
    const a = $("#find-input").value, b = $("#replace-input").value; if (!a) return;
    inp.value = inp.value.replace(a, b); inp.dispatchEvent(new Event("input"));
  });
  $("#replace-all").addEventListener("click", () => {
    const a = $("#find-input").value, b = $("#replace-input").value; if (!a) return;
    inp.value = inp.value.split(a).join(b); inp.dispatchEvent(new Event("input"));
  });

  $("#ctx-rename").addEventListener("click", async () => {
    const t = State.tabs.find(x => x.id === State.ctxTab); if (!t) return;
    const n = await uiPrompt("New tab name:", t.title);
    if (n?.trim()) { t.title = n.trim(); renderTabs(); }
  });
  $("#ctx-dup").addEventListener("click", () => {
    const t = State.tabs.find(x => x.id === State.ctxTab);
    if (t) createTab(`${t.title} (copy)`, t.content, t.scriptId);
  });
  $("#ctx-autoexec").addEventListener("click", async () => {
    const t = State.tabs.find(x => x.id === State.ctxTab); if (!t) return;
    const f = /\.(luau|lua|txt)$/.test(t.title) ? t.title : `${t.title}.luau`;
    const r = await api("save_script_file", { filename: "autoexec/" + f, content: t.content });
    if (r?.ok) { State.scripts.push({ id:`disk_AutoExec_${Date.now()}`, title:f, folder:"AutoExec", content:t.content }); renderExplorerBody(); }
  });
  $("#ctx-close-others").addEventListener("click", () => {
    const keep = State.tabs.find(x => x.id === State.ctxTab);
    if (keep) { State.tabs = [keep]; selectTab(keep.id); }
  });
  $("#ctx-close").addEventListener("click", () => { if (State.ctxTab) closeTab(State.ctxTab); });

  $("#file-ctx-open").addEventListener("click", () => {
    const s = State.scripts.find(x => x.id === State.ctxFileId);
    $("#file-ctx").classList.remove("open"); if (s) openScript(s);
  });
  $("#file-ctx-rename").addEventListener("click", async () => {
    const s = State.scripts.find(x => x.id === State.ctxFileId);
    $("#file-ctx").classList.remove("open"); if (!s) return;
    const n = await uiPrompt("New filename:", s.title);
    if (!n) return;
    const safe = /\.(lua|luau|txt)$/i.test(n) ? n : `${n}.luau`;
    if (String(s.id).startsWith("disk_")) {
      const r = await api("manage_script_file", { folder:"Scripts", action:"rename", filename:s.title, newFilename:safe });
      if (r?.ok) s.title = r.filename;
    } else s.title = safe;
    renderExplorerBody();
  });
  $("#file-ctx-disable").addEventListener("click", async () => {
    const s = State.scripts.find(x => x.id === State.ctxFileId);
    $("#file-ctx").classList.remove("open"); if (!s) return;
    if (String(s.id).startsWith("disk_")) {
      const r = await api("manage_script_file", { folder:"AutoExec", action:"disable", filename:s.title });
      if (r?.ok) { s.title = r.filename; s.disabled = true; renderExplorerBody(); }
    }
  });
  $("#file-ctx-remove").addEventListener("click", async () => {
    const s = State.scripts.find(x => x.id === State.ctxFileId);
    $("#file-ctx").classList.remove("open"); if (!s) return;
    if (String(s.id).startsWith("disk_")) {
      const f = (s.folder||"").toLowerCase().startsWith("autoexec") ? "AutoExec" : "Scripts";
      await api("manage_script_file", { folder:f, action:"delete", filename:s.title });
    }
    State.scripts = State.scripts.filter(x => x.id !== s.id);
    renderExplorerBody();
  });

  const closeClients = () => { $("#clients").classList.remove("open"); $("#clients-backdrop").classList.remove("open"); };
  $("#clients-close").addEventListener("click", closeClients);
  $("#clients-backdrop").addEventListener("click", closeClients);

  $("#cmd-back").addEventListener("click", (ev) => { if (ev.target.id === "cmd-back") $("#cmd-back").classList.remove("open"); });
  $("#cmd-input").addEventListener("input", (e) => renderCmdList(e.target.value));
  $("#cmd-input").addEventListener("keydown", (e) => {
    if (e.key === "Escape") $("#cmd-back").classList.remove("open");
    if (e.key === "Enter") $("#cmd-list .cmd-row")?.click();
  });
  $("#settings-search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    $$("#settings-body .s-row").forEach(r => { r.style.display = !q || r.innerText.toLowerCase().includes(q) ? "" : "none"; });
  });
  $("#settings-back").addEventListener("click", () => switchView("editor"));

  $("#qa-new").addEventListener("click", () => { switchView("editor"); createTab(); });
  $("#qa-attach").addEventListener("click", () => doAttach());
  $("#qa-launch-inject").addEventListener("click", () => doLaunchInject(""));
  $("#qa-settings").addEventListener("click", () => switchView("settings"));

  $("#pick-script").addEventListener("change", (e) => {
    const f = e.target.files?.[0]; if (!f) return;
    const r = new FileReader();
    r.onload = () => createTab(f.name, String(r.result || ""));
    r.readAsText(f);
  });
  $("#pick-image").addEventListener("change", async (e) => {
    const f = e.target.files?.[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const url = String(r.result || "");
      const saved = await api("save_custom_theme_image", { filename: f.name, dataUrl: url });
      if (saved?.ok) { State.settings = saved.settings; await patchSettings({ appearance: { useBackgroundImage: true } }); renderSettingsBody(); }
    };
    r.readAsDataURL(f);
  });
  $("#pick-avatar").addEventListener("change", async (e) => {
    const f = e.target.files?.[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const url = String(r.result || "");
      const res = await api("save_profile_image", { dataUrl: url });
      if (res?.ok) { State.profilePicture = url; renderExplorerBody(); }
    };
    r.readAsDataURL(f);
  });
  $("#pick-json").addEventListener("change", async (e) => {
    const f = e.target.files?.[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const res = await api("import_settings_json", { json: String(r.result || "") });
      if (res?.ok) { State.settings = res.settings; applySettings(); }
    };
    r.readAsText(f);
  });

  const grip = $("#resize-grip");
  grip.addEventListener("pointerdown", async (ev) => {
    ev.preventDefault();
    const rect = await api("window_get_rect");
    const sx = ev.screenX, sy = ev.screenY;
    const sw = rect?.width || 1180, sh = rect?.height || 720;
    let pending = false;
    const move = async (me) => {
      if (pending) return; pending = true;
      requestAnimationFrame(async () => {
        const nw = Math.max(880, sw + (me.screenX - sx));
        const nh = Math.max(520, sh + (me.screenY - sy));
        await api("window_resize", { width: nw, height: nh }); pending = false;
      });
    };
    const up = () => { window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); };
    window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
  });

  window.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") { e.preventDefault(); $("#rail-execute").click(); return; }
    if (e.ctrlKey && (e.key === "b" || e.key === "B")) { e.preventDefault(); handleActivityClick(State.lastActivity); return; }
    if (e.ctrlKey && e.key === "k") { e.preventDefault(); openCmd(); return; }
    if (e.ctrlKey && e.key === "s") { e.preventDefault(); $("#tb-save").click(); return; }
    if (e.ctrlKey && e.key === "n") { e.preventDefault(); createTab(); return; }
    if (e.ctrlKey && e.key === "w") { e.preventDefault(); if (State.activeTab) closeTab(State.activeTab); return; }
    if (e.ctrlKey && e.key === "f") { e.preventDefault(); openFind(false); return; }
    if (e.ctrlKey && e.key === "h") { e.preventDefault(); openFind(true); return; }
    if (e.ctrlKey && e.key === "j") { e.preventDefault(); patchSettings({ console: { showConsole: !State.settings.console.showConsole } }); return; }
  });
}

async function showClients() {
  const d = $("#clients"), b = $("#clients-backdrop"), l = $("#clients-list");
  b.classList.add("open"); d.classList.add("open");
  l.innerHTML = `<div class="clients-empty"><h3>Scanning...</h3></div>`;
  const r = await api("get_status");
  if (r?.pids?.length) {
    l.innerHTML = "";
    r.pids.forEach(pid => {
      const row = document.createElement("div"); row.className = "client-row";
      const isAtt = r.attached_pid === pid;
      row.innerHTML = `<div class="client-info"><span class="client-pid">PID ${pid}</span><span class="client-state${isAtt ? " attached" : ""}">${isAtt ? `Attached (${r.attached_version || "?"})` : "Not attached"}</span></div><button class="client-attach"${isAtt ? " disabled" : ""}>${isAtt ? "Attached" : "Attach"}</button>`;
      if (!isAtt) {
        row.querySelector(".client-attach").addEventListener("click", async () => {
          await doAttach(pid); showClients();
        });
      }
      l.appendChild(row);
    });
  } else {
    l.innerHTML = `<div class="clients-empty"><h3>No Roblox running</h3><p>Launch Roblox and it will appear here, or use Launch &amp; Inject.</p></div>`;
  }
}

async function boot() {
  if (State.booted) return; State.booted = true;
  try {
    const init = await api("get_initial_state");
    if (init?.ok) {
      State.settings = init.settings || {};
      State.builtinThemes = init.builtinThemes || {};
      State.scripts = init.scripts || [];
      State.app = init.app || {};
      State.profilePicture = init.profilePicture || null;
      State.offsets = init.offsets || {};
      State.versions = init.installedVersions || [];
      State.explorerVisible = State.settings.console?.leftExplorerVisible !== false;
      State.lastActivity = State.settings.console?.lastActivity || "explorer";
      setAttached(!!init.attached);
    }
    const g = State.settings.general || {};
    $("#home-user").textContent = g.userName || "—";
    $("#home-plan").textContent = g.planName || "—";
    $("#home-license").textContent = g.licenseStatus || "Active";
    $("#home-expires").textContent = g.licenseExpires || "Never";
    $("#home-dll").textContent = State.offsets?.dll_found ? "found" : "missing";
    $("#home-offsets").textContent = State.offsets?.cached_version || "not cached";
    $("#home-versions").textContent = (State.versions?.length || 0) + " installed";
    $("#home-newest").textContent = State.versions?.[0]?.name || "—";

    applyTheme();
    renderTabs();
    wireAll();
    attachFxLayers();
    applySettings();

    if (State.scripts.length) createTab(State.scripts[0].title, State.scripts[0].content, State.scripts[0].id);
    else createTab("Untitled", "-- Untitled Script\n");

    logMessage("terminal", `Kitty v${State.app.version || "4.6.0"} ready`, "ok");
    logMessage("terminal", State.offsets?.dll_found ? `Module.dll: ${State.offsets.dll_path}` : "Module.dll not found — put it next to kitty.py", State.offsets?.dll_found ? "info" : "warn");
    logMessage("terminal", `Offsets: ${State.offsets?.cached_version || "not cached"}`, "info");
    logMessage("terminal", `Installed versions: ${State.versions?.length || 0}`, "info");
  } catch (err) {
    console.error("[boot]", err);
    if (!State.settings) State.settings = { appearance:{}, effects:{}, editor:{}, console:{}, general:{}, secret:{} };
    try { applySettings(); } catch(_) {}
  } finally {
    const f = $("#load-fill");
    if (f) f.style.width = "100%";
    setTimeout(() => {
      const l = $("#loading");
      if (l) { l.classList.add("hidden"); setTimeout(() => l.style.display = "none", 400); }
    }, 350);
  }
  setInterval(async () => {
    try {
      const r = await api("get_status");
      if (r && !!r.attached !== State.attached) setAttached(!!r.attached, r.attached_pid, r.attached_version, r.attached_method);
    } catch {}
  }, 4000);
}

if (window.pywebview && window.pywebview.api) boot();
else {
  window.addEventListener("pywebviewready", boot, { once: true });
  window.addEventListener("DOMContentLoaded", () => setTimeout(boot, 200), { once: true });
}
})();
</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  API BRIDGE + FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

class ApiBridge:
    def __init__(self, backend): self._b = backend
    def get_initial_state(self, _p=None): return self._b.get_initial_state()
    def update_settings(self, p=None): return self._b.update_settings(p if isinstance(p, dict) else {})
    def reset_all_settings(self, _p=None): return self._b.reset_all_settings()
    def sync_offsets(self, p=None):
        force = bool((p or {}).get("force", True)) if isinstance(p, dict) else True
        return self._b.sync_offsets(force=force)
    def offsets_status(self, _p=None): return self._b.offsets_status()
    def pick_theme_image(self, _p=None): return self._b.pick_theme_image()
    def pick_profile_image(self, _p=None): return self._b.pick_profile_image()
    def save_profile_image(self, p=None): return self._b.save_profile_image(p if isinstance(p, dict) else {})
    def remove_profile_image(self, _p=None): return self._b.remove_profile_image()
    def save_custom_theme_image(self, p=None): return self._b.save_custom_theme_image(p if isinstance(p, dict) else {})
    def remove_custom_theme_image(self, _p=None): return self._b.remove_custom_theme_image()
    def clear_theme_cache(self, _p=None): return self._b.clear_theme_cache()
    def open_script_file(self, _p=None): return self._b.open_script_file()
    def save_script_file(self, p=None): return self._b.save_script_file(p if isinstance(p, dict) else {})
    def manage_script_file(self, p=None): return self._b.manage_script_file(p if isinstance(p, dict) else {})
    def export_settings_json(self, _p=None): return self._b.export_settings_json()
    def import_settings_json(self, p=None): return self._b.import_settings_json(p if isinstance(p, dict) else {})
    def open_data_folder(self, _p=None): return self._b.open_data_folder()
    def simulate_attach(self, p=None):
        pid = None
        if isinstance(p, dict): pid = p.get("pid")
        return self._b.simulate_attach(pid)
    def launch_and_inject(self, p=None):
        version = str((p or {}).get("version", "")) if isinstance(p, dict) else ""
        return self._b.launch_and_inject(version)
    def simulate_execute(self, p=None): return self._b.simulate_execute(p if isinstance(p, dict) else {})
    def kill_roblox(self, _p=None): return self._b.kill_roblox()
    def get_status(self, _p=None): return self._b.get_status()
    def window_minimize(self, _p=None): return self._b.window_minimize()
    def window_maximize(self, _p=None): return self._b.window_maximize()
    def window_resize(self, p=None): return self._b.window_resize(p if isinstance(p, dict) else {})
    def window_get_rect(self, _p=None): return self._b.window_get_rect()
    def window_close(self, _p=None): return self._b.window_close()


def run_http_fallback(backend):
    backend.runtime_mode = "browser"; bridge = ApiBridge(backend)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a): return
        def _json(self, code, data):
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            if urllib.parse.urlparse(self.path).path in ("/", "/index.html"):
                raw = KITTY_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers(); self.wfile.write(raw); return
            self._json(404, {"ok": False})
        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path
            if not path.startswith("/api/"): self._json(404, {"ok": False}); return
            method = path[len("/api/"):].strip("/")
            size = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(size) if size > 0 else b"{}"
            try: payload = json.loads(body.decode("utf-8")) if body else {}
            except Exception: payload = {}
            fn = getattr(bridge, method, None)
            if not callable(fn): self._json(404, {"ok": False, "error": f"Unknown {method}"}); return
            self._json(200, fn(payload))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"[{APP_NAME}] Fallback at {url}")
    threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()


def _enable_ansi():
    if os.name != "nt": return
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11)
        mode = ctypes.wintypes.DWORD()
        if k32.GetConsoleMode(h, ctypes.byref(mode)):
            k32.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:
        pass


def print_banner():
    _enable_ansi()
    C = "\033[38;5;216m"; N = "\033[38;5;110m"; D = "\033[38;5;240m"
    A = "\033[38;5;141m"; OK = "\033[38;5;114m"; BAD = "\033[38;5;210m"; R = "\033[0m"
    print()
    print(f"{C}     /\\_/\\     {N}██ ██ ██  ████████  ████████  ██    ██{R}")
    print(f"{C}    ( {A}o.o{C} )    {N}██ ██ ██     ██        ██     ██    ██{R}")
    print(f"{C}     > ^ <     {N}██ ██████     ██        ██     ██    ██{R}")
    print(f"{C}    /     \\    {N}██ ██ ██     ██        ██       ██  ██{R}")
    print(f"{C}   (_|___|_)   {N}██ ██ ██     ██        ██         ██{R}")
    print()
    print(f"  {D}Kitty{R} {N}v{APP_VERSION}{R}  {D}·{R}  {D}premium Roblox workspace{R}")
    print(f"  {D}{'─' * 56}{R}")
    print(f"  {D}runtime{R}    {APP_RUNTIME_DIR}")
    print(f"  {D}module{R}     {_resolve_dll() or 'NOT FOUND'}")
    print(f"  {D}platform{R}   {platform.system()} {platform.release()}")
    print(f"  {D}python{R}     {platform.python_version()}")
    print(f"  {D}pywebview{R}  {OK+'yes'+R if HAS_PYWEBVIEW else BAD+'no'+R}")
    print(f"  {D}pillow{R}     {OK+'yes'+R if HAS_PIL else BAD+'no'+R}")
    print(f"  {D}pystray{R}    {OK+'yes'+R if HAS_PYSTRAY else BAD+'no'+R}")
    print(f"  {D}psutil{R}     {OK+'yes'+R if HAS_PSUTIL else BAD+'no'+R}")
    installed = list_installed_versions()
    print(f"  {D}versions{R}   {len(installed)} installed" + (f" (newest: {installed[0]['name']})" if installed else ""))
    print(f"  {D}{'─' * 56}{R}")
    print()


def _print_pywebview_help():
    print("="*72)
    print(f"[{APP_NAME}] pywebview failed to start.")
    print("")
    print("  Install WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703")
    print("  Then: pip install pywebview")
    print("")
    print("  Or run: python kitty.py --browser")
    print("="*72)


def main():
    global _main_window
    print_banner()
    argv = sys.argv[1:]
    if "--browser" in argv:
        run_http_fallback(KittyBackend()); return
    if not HAS_PYWEBVIEW:
        print("pywebview not installed. pip install pywebview  OR  python kitty.py --browser")
        sys.exit(1)
    backend = KittyBackend(); init_system_tray()
    gen = backend.settings.get("general", {})
    start_global_hotkey(str(gen.get("globalToggleKey", "Insert")))
    apply_process_priority_win32(str(gen.get("performanceMode", "medium")))
    try:
        bridge = ApiBridge(backend)
        _main_window = webview.create_window(
            title="Spotify" if gen.get("disguiseMode") else APP_NAME,
            html=KITTY_HTML, js_api=bridge,
            width=1180, height=720, min_size=(880, 520),
            frameless=True, easy_drag=False, background_color="#f4ede1")
        if gen.get("streamproof"):
            threading.Timer(1.2, lambda: apply_streamproof_win32(True)).start()
        if gen.get("launchMaximized"):
            threading.Timer(0.5, lambda: _main_window.maximize() if _main_window else None).start()
        webview.start(debug=False)
        stop_global_hotkey()
        return
    except Exception as exc:
        print(f"[{APP_NAME}] pywebview raised: {exc}")
        if "--force" in argv:
            run_http_fallback(backend); return
        _print_pywebview_help(); sys.exit(1)


if __name__ == "__main__":
    main()