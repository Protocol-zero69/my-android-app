[app]
title = Survey Assistant
package.name = surveyassistant
package.domain = org.angrybids
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.3.1,pyjnius==1.7.0,sqlite3
orientation = portrait
fullscreen = 0

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
