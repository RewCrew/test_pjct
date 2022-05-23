import logging
import sys
from typing import Optional

import jwt

from classic.app import DTO, validate_with_dto
from pydantic import validate_arguments
from classic.aspects import PointCut
from classic.components import component
from classic.messaging import Message, Publisher

from user_service.application import errors, interfaces
from user_service.application.dataclasses import User

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)

join_points = PointCut()
join_point = join_points.join_point


class UserInfo(DTO):
    name: str
    email: str
    balance: Optional[int] = 0

class UserUpdate(DTO):
    name: Optional[str] = None
    email: Optional[str] = None
    id: Optional[int] = None
    balance: Optional[int] = 0

class UserData(DTO):
    user_id: Optional[int]
    amount: Optional[int]
    type: Optional[str]

@component
class UsersService:
    user_repo: interfaces.UsersRepo
    publisher: Publisher

    @join_point
    @validate_with_dto
    def add_user(self, user_info: UserInfo):
        new_user = user_info.create_obj(User)
        user = self.user_repo.get_or_create(new_user)

        token = jwt.encode(
            {
                "sub": user.id,
                "name": user.name,
                "email": user.email,
                "login": user.name,
                "group": "User"
            },
            'kerim_project',
            algorithm='HS256'
        )
        return token

    @join_point
    def get_user(self, id: int):
        user = self.user_repo.get_by_id(id)
        if user is None or user.id != id:
            raise errors.ErrorUser(message="No user exist")
        else:
            return user

    @join_point
    def message_sender(self, data: dict):
        pass


    @join_point
    @validate_arguments
    def change_balance(self, user_id:int, amount:int, type:str):
        result = {'user_id': user_id, 'amount':amount, 'type':type }
        self.publisher.publish(
            Message("UserExchange", {"data":result})
        )

    @join_point
    @validate_arguments
    def change_balance_sql(self, data:dict):
        new_data = UserData(**data)
        user = self.get_user(new_data.user_id)
        if new_data.type == 'withdraw':
            if user.balance >= new_data.amount:
                user.balance -= new_data.amount
                print( f'you withdraw {new_data.amount} from your balance')
            else:
                raise errors.ErrorUser(message=f'you dont have enough credits on your balance to withdraw {new_data.amount}')
        elif new_data.type == 'deposit':
            user.balance += new_data.amount
            print( f'you deposit {new_data.amount} on your balance')
