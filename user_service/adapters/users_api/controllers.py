from falcon import Request, Response

from classic.components import component
from classic.http_auth import authenticator_needed, authenticate

from user_service.adapters.users_api.join_points import join_point
from user_service.application import services


@authenticator_needed
@component
class Users:
    users: services.UsersService

    @join_point
    def on_post_register(self, request: Request, response: Response):
        token = self.users.add_user(**request.media)
        response.media = {"Token": token}

    @authenticate
    @join_point
    def on_post_change_balance(self, request: Request, response: Response):
        request.media['user_id'] = request.context.client.user_id
        resp = self.users.change_balance(**request.media)
        response.media={'message': 'see console for transaction status'}