from marshmallow import Schema, fields


class RequestBodySchema(Schema):
    pass


class AuthenticateUserRequest(RequestBodySchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class EmptyBodySchema(RequestBodySchema):
    pass
