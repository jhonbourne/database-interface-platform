import pytest

# Import the module under test
import backend.repositories.user_info as user_info_module

class FakeConn:
    def __init__(self, rows, columns):
        # rows should be a tuple of tuples, columns a list
        self._rows = rows
        self._columns = columns
    def select(self, table_name, column_names='*', where='all', where_params=(), **kwargs):
        return self._rows, self._columns
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False

class FakeMySqlHelper:
    def __init__(self, user=None, password=None, database=None):
        # We'll just ignore params and provide a fake connection object
        pass
    def __enter__(self):
        # default user row: username, password (hashed), id
        return FakeConn((("alice", "hashed_pw", 42),), ["username","password","id"])
    def __exit__(self, *args):
        return False

def test_verify_user_success(monkeypatch):
    # Arrange: patch MySqlHelper and check_password_hash
    monkeypatch.setattr(user_info_module, 'MySqlHelper', FakeMySqlHelper)
    monkeypatch.setattr(user_info_module, 'check_password_hash', lambda stored, provided: True)

    # Act
    result = user_info_module.verify_user('alice', 'password123')

    # Assert
    assert result['username'] == 'alice'
    assert result['id'] == 42


def test_verify_user_incorrect_password(monkeypatch):
    # Arrange: patch MySqlHelper to return a user but check_password_hash returns False
    monkeypatch.setattr(user_info_module, 'MySqlHelper', FakeMySqlHelper)
    monkeypatch.setattr(user_info_module, 'check_password_hash', lambda stored, provided: False)

    # Act / Assert
    with pytest.raises(Exception) as excinfo:
        user_info_module.verify_user('alice', 'wrongpass')
    assert 'Incorrect password' in str(excinfo.value)


def test_verify_user_not_found(monkeypatch):
    # Arrange: patch MySqlHelper to return no rows
    class EmptyConn(FakeMySqlHelper):
        def __enter__(self):
            return FakeConn(tuple(), ["username","password","id"])
    monkeypatch.setattr(user_info_module, 'MySqlHelper', EmptyConn)
    monkeypatch.setattr(user_info_module, 'check_password_hash', lambda stored, provided: False)

    # Act / Assert
    with pytest.raises(Exception) as excinfo:
        user_info_module.verify_user('bob', 'whatever')
    assert 'User not found' in str(excinfo.value)
