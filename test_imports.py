# test_imports.py
import faulthandler
faulthandler.enable()

print("1) start")

try:
    import flask
    print("2) flask OK")
except Exception as e:
    print("2) flask EXCEPT:", repr(e))

try:
    import database
    print("3) database OK")
except Exception as e:
    print("3) database EXCEPT:", repr(e))

try:
    import speech_recognition_module
    print("4) speech_recognition_module OK")
except Exception as e:
    print("4) speech_recognition_module EXCEPT:", repr(e))

try:
    import gps_module
    print("5) gps_module OK")
except Exception as e:
    print("5) gps_module EXCEPT:", repr(e))

try:
    import voice_record
    print("6) voice_record OK")
except Exception as e:
    print("6) voice_record EXCEPT:", repr(e))

try:
    import mailer
    print("7) mailer OK")
except Exception as e:
    print("7) mailer EXCEPT:", repr(e))

print("done")
