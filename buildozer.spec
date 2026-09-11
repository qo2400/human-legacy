[app]
title = Human Legacy
package.name = humanlegacy
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Android permission needed only if you later add file export/import
# beyond the app's private data directory. Not required for normal
# save/load, since human_legacy.py stores its save file in the app's
# private user_data_dir.
# android.permissions = WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
