[app]
title = Chouhan SUPER APP
package.name = chouhanmyrasuperapp
package.domain = com.chouhan.myra
source.dir =.
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy==2.2.0,requests,python-dotenv
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license_agreements = True

[buildozer]
log_level = 1
warn_on_root = 1
