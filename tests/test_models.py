from sqlalchemy import select

from fastapizero.models import User


def test_create_user(session):
    user = User(
        username='xLost',
        email='xlost@email.com',
        password='senha123',
    )

    session.add(user)
    session.commit()
    result = session.scalar(
        select(User).where(User.email == 'xlost@email.com')
    )

    assert result.username == 'xLost'
