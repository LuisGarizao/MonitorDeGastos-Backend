from rest_framework.exceptions import APIException

class UnauthorizedAccess(APIException):
    status_code = 403
    default_code = "access_not_authorized"
    default_detail = "credentials missing or invalid for accessing this resource."


class ExpenseNotFound(APIException):
    status_code = 404
    default_code = "expense_not_found"
    default_detail = "The requested expense was not found."


class InvalidDateRange(APIException):
    status_code = 400
    default_code = "invalid_date_range"
    default_detail = "The start date cannot be greater than the end date."


class ConflictingParams(APIException):
    status_code = 400
    default_code = "conflicting_query_params"
    default_detail = "Some of the query params have conflict."    

class InvalidParamValue(APIException):
    status_code = 400
    default_code = "invalid_query_param_value"
    default_detail = "provided value for a query parameter is not valid."    
    