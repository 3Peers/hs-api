OTP_EXPIRY_SECONDS = 300
OTP_MAX_ATTEMPTS = 5
OTP_MAX_RESENDS = 3

EMAIL_BLOCK_SECONDS = 7200


class ResponseMessages(object):
    TEMPORARY_BLOCKED_EMAIL = 'This email has been temporarily blocked.' \
        ' Please try after some time'
    BAD_CLIENT = 'Unrecognized Client'
    INVALID_OTP = 'Entered OTP wrong. Please Try Again.'
    OTP_ATTEMPT_EXCEEDED = 'OTP attempts limit exceeded. Please try after some time.'
    OTP_RESENDS_EXCEEDED = 'OTP resends limit exceeded. Please try after some time.'
    OTP_SUCCESS = 'OTP Sent Successfully.'
    OTP_EXPIRED = 'OTP has expired'
    RESET_PASSWORD_SUCCESS = 'Password Reset Successfully'
    BAD_PASSWORD_PROVIDED = 'Bad Password Provided. Please follow good password practices'
    NO_USER_FOUND = 'No User Found'
    USER_WITH_EMAIL_EXISTS = 'User with this email already exists!'
    INVALID_PASSWORD = 'Invalid password.'
