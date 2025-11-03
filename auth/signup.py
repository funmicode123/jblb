from blockchain.services.hedera_service import create_user_account
from users.models import User

def create_user_account(data):
    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"]
    )

    # create Hedera wallet
    hedera_data = create_user_account()
    user.hedera_account_id = hedera_data["account_id"]
    user.hedera_private_key = hedera_data["private_key"]
    user.save()
    return user
