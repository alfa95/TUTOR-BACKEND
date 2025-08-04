from src.db.mongo_utils import create_user, get_user_by_email

if __name__ == "__main__":
    try:
       test_create_and_get_user()
    except Exception as e:
        print("❌ Error:", e)

def test_create_and_get_user():
    email = "as4195@gmail.com"
    name = "Anurag"
    create_user(email, name)
    user = get_user_by_email(email)

    assert user is not None
    assert user["email"] == email
