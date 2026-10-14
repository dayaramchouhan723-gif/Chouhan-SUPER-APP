[app]

title = Chouhan SUPER APP
package.name = chouhansuperapp
package.domain = com.chouhan
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json
source.exclude_dirs = tests,docs,bin,dist,build,.pytest_cache,__pycache__
version = 0.1.0
requirements = python3,kivy,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 36
android.minapi = 24
android.ndk = 28c
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
