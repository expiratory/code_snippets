from app.validators.password import validate_password_strength


def test_validate_password_strength_valid():
    is_valid, errors = validate_password_strength("StrongPass1!")
    assert is_valid is True
    assert len(errors) == 0


def test_validate_password_strength_too_short():
    is_valid, errors = validate_password_strength("Short1!")
    assert is_valid is False
    assert "Password must be at least 8 characters long" in errors


def test_validate_password_strength_no_uppercase():
    is_valid, errors = validate_password_strength("weakpass1!")
    assert is_valid is False
    assert "Password must contain at least one uppercase letter" in errors


def test_validate_password_strength_no_lowercase():
    is_valid, errors = validate_password_strength("WEAKPASS1!")
    assert is_valid is False
    assert "Password must contain at least one lowercase letter" in errors


def test_validate_password_strength_no_digit():
    is_valid, errors = validate_password_strength("WeakPass!")
    assert is_valid is False
    assert "Password must contain at least one digit" in errors


def test_validate_password_strength_no_special():
    is_valid, errors = validate_password_strength("WeakPass1")
    assert is_valid is False
    assert (
        'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
        in errors
    )


def test_validate_password_strength_repeating():
    is_valid, errors = validate_password_strength("Aaaaa123!")
    assert is_valid is False
    assert "Password contains too many repeating characters" in errors


def test_validate_password_strength_sequential():
    is_valid, errors = validate_password_strength("Abcdef1!")
    assert is_valid is False
    assert "Password contains sequential characters" in errors

    is_valid, errors = validate_password_strength("12345Ab!")
    assert is_valid is False
    assert "Password contains sequential characters" in errors
