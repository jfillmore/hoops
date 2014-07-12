import copy


import hoops.status

VERSION = "1.0.0"

response_template = {
    "api_version": VERSION,
    "response_data": None,
    "status_code": None,
    "status_message": None,
}


class APIResponse(object):
    response = None
    status = None

    def __init__(self, data, extra=None, status=None):
        self.response = copy.deepcopy(response_template)
        self.response["response_data"] = data
        if extra:
            self.response.update(extra)
        self.status = status if status else hoops.status.library.API_OK
        self.response.update(self.status.get_dict())

    def __call__(self):
        return self.response

    def to_json(self):
        return self.response


class PaginatedAPIResponse(APIResponse):

    def __init__(self, data, pagination=None, params=None, extra=None, status=None):

        if extra is None:
            extra = {}

        if pagination:
            offset = pagination.per_page * (pagination.page - 1)
            extra["pagination"] = {
                "page": pagination.page,
                "limit": pagination.per_page,
                "next_page": (
                    pagination.page + 1
                    if offset + pagination.per_page < pagination.total
                    else None),
                "total": pagination.total,
                "sort_by": params.get('sort_by', 'id'),
                "sort_dir": params.get('sort_dir', 'asc'),
            }

        super(PaginatedAPIResponse, self).__init__(data, extra, status)
