from slotomania.contrib.jwt_auth import AuthenticateUser
from slotomania.core import InstructorView as BaseView


class InstructorView(BaseView):
    routes = {"LoginApp": AuthenticateUser}
