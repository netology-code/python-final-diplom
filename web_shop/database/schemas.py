"""Database tables' schemas."""
from web_shop import ma
from web_shop.database import User


class UserFullSchema(ma.Schema):
    """User-model full schema for admins."""

    class Meta:
        model = User
        fields = "username password email is_admin token expires_at".split()


class UserSchema(ma.Schema):
    """User-model schema for users."""

    class Meta:
        model = User
        fields = "username email is_admin".split()


#
# class AdSchema(ma.Schema):
#     class Meta:
#         model = Advertisement
#         fields = "id title description created modified owner".split()
#
#     owner = ma. Nested(UserSchema)

#
# ad_schema = AdSchema()
# ads_schema = AdSchema(many=True)


user_full_schema = UserFullSchema()
users_full_schema = UserFullSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
