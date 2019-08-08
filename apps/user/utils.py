def get_verification_message_with_code(code: str):
    verification_message = f'''Hi, you have requested to sign-up on HS.

This is your OTP: {code}.

Please keep it confidential and don't share with anyone.

Thanks,
Team HS
'''

    return verification_message
