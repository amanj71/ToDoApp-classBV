from datetime import timedelta
from rest_framework_simplejwt.tokens import Token

# create token classes here
class ActivationToken(Token):
    token_type = "activation"
    lifetime = timedelta(hours=24)

class ResetPasswordToken(Token):
    token_type = 'reset-password'
    lifetime = timedelta(hours=2)

#create token generation functions here
def create_activation_token(user):
    token = ActivationToken.for_user(user)
    token["purpose"] = "activation"
    return str(token)

def create_reset_password_token(user):
    token = ResetPasswordToken.for_user(user)
    token["purpose"] = "reset-password"
    return str(token)

