"""
Custom exception handler for consistent API error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': _get_error_message(response),
                'details': response.data,
            }
        }
        response.data = error_data

    return response


def _get_error_message(response):
    """Extract a human-readable error message from the response."""
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        return 'Validation error. Please check your input.'
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        return 'Authentication credentials were not provided or are invalid.'
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        return 'You do not have permission to perform this action.'
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        return 'The requested resource was not found.'
    elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return 'Method not allowed.'
    elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        return 'An internal server error occurred.'
    return 'An error occurred.'
