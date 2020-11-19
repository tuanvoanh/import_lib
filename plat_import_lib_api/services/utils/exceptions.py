from rest_framework.exceptions import APIException
from rest_framework import status


class GenericException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    code = 1000
    summary = 'Error'
    verbose = False

    def __init__(self, message=None, status_code=400):
        if not message:
            message = 'We hit a snag. Please check your internet connection and try'
        if status:
            self.status_code = status_code
        super().__init__(message)

    def serialize(self):
        return {
            'code': self.code,
            'message': self.detail,
            'summary': self.summary
        }


class InvalidFormatException(GenericException):
    message = 'Invalid request params'
    summary = 'Invalid Format Exception'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)


class InvalidImportDataObjectException(GenericException):
    message = 'Invalid Data Import Temporary'
    summary = 'Invalid Import Data Exception'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)


class InvalidFileTypeException(GenericException):
    message = 'Invalid File Type'
    summary = 'Invalid File Type'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)


class InvalidParamException(GenericException):
    message = 'Invalid Parameter Request'
    summary = 'Invalid Parameter Request'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)


class InvalidModuleException(GenericException):
    message = 'Invalid module request'
    summary = 'Invalid Module Exception'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)


class InvalidExportModuleException(GenericException):
    message = 'Invalid export module request'
    summary = 'Invalid  Export Module Exception'

    def __init__(self, message=None, verbose=False):
        self.verbose = verbose
        if message:
            self.message = message
        super().__init__(message=self.message)
