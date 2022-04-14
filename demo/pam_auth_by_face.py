"""
login account   requisite   pam_python.so pam_auth_by_face.py
login auth      requisite   pam_python.so pam_auth_by_face.py
login password  requisite   pam_python.so pam_auth_by_face.py
login session   requisite   pam_python.so pam_auth_by_face.py
"""
from demo.AuthByFace import AuthByFace

DEFAULT_USER = "nobody"


def pam_sm_authenticate(pamh, flags, argv):
    # try:
    #     user = pamh.get_user(None)
    # except pamh.exception as e:
    #     return e.pam_result
    # if user == None:
    #     pamh.user = DEFAULT_USER
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS


def pam_sm_setcred(pamh, flags, argv):
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS


def pam_sm_open_session(pamh, flags, argv):
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    if AuthByFace(False, False).isAuthSuccess():
        return pamh.PAM_SUCCESS
