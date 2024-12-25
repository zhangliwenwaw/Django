from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from common.customresponse import CustomResponse


def CustomResponseExceptionHandler(exc, context):
    # 调用默认的异常处理函数
    response = exception_handler(exc, context)

    # 检查是否是JWT令牌过期的异常
    if isinstance(exc, (TokenError, InvalidToken)) and 'token_not_valid' in str(exc):
        # 返回自定义的响应
        return CustomResponse(code=401, msg={"detail": "Token has expired."}, data=response.data, status=status.HTTP_401_UNAUTHORIZED)

    return response
