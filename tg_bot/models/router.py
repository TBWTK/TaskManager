from tortoise import Tortoise


async def init_database():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": 'tg_bot',
                        "host": "db",
                        "password": "postgres",
                        "port": 5432,
                        "user": "postgres",
                    }
                },
            },
            "apps": {
                "models": {
                    "models": ["tg_bot.models.models"],
                    "default_connection": "default",
                },
            },
        }
    )
    await Tortoise.generate_schemas()
