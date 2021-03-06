from kombu import Connection

from classic.messaging_kombu import KombuConsumer

from user_service.application import services

from .scheme import broker_scheme


def create_consumer(
    connection: Connection, users: services.UsersService
) -> KombuConsumer:
    consumer = KombuConsumer(connection=connection, scheme=broker_scheme)

    consumer.register_function(
        users.change_balance_sql,
        'UserQueue',
    )

    return consumer
