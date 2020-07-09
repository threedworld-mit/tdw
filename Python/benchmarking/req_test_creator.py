import os
os.chdir("..")
from release_creator import build_utility_application


"""
Create the ReqTest application.
"""


build_utility_application("Windows", "ReqTest", "Assets/TDWTest/ReqTest.unity", "TEST")
