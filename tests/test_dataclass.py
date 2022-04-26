from dataclasses import dataclass

import marshmallow_dataclass
from marshmallow import post_dump, pre_load


@marshmallow_dataclass.add_schema
@dataclass
class ResponseStatus:
    code: int
    message: str

    def __repr__(self) -> str:
        return ResponseStatus.Schema().dumps(self)  # type: ignore

    @classmethod
    def from_str(cls, data: str) -> "ResponseStatus":
        """Convert a str to a ResponseStatus."""
        space = data.find(" ")
        if space == -1:
            code = None
        else:
            try:
                code = int(data[:space])
                data = data[space + 1 :]
            except ValueError:
                code = None

        return ResponseStatus(code, data)  # type: ignore

    @post_dump
    def __render_status(self, data, many):
        if many:
            _result = [str(ResponseStatus(**x)) for x in data]
        else:
            _result = str(ResponseStatus(**data))
        return _result

    @pre_load
    def __parse_status(self, data, many, partial):
        if many:
            _result = [ResponseStatus.from_str(x).__dict__ for x in data]
        else:
            _result = ResponseStatus.from_str(data).__dict__
        return _result

    def is_successful(self) -> bool:
        """Check if the status code is in the range [200, 300)."""
        return self.code is not None and self.code >= 200 and self.code < 300

    def __str__(self) -> str:
        return f"{self.code} {self.message}"


r = ResponseStatus.from_str("200 OK")
print(ResponseStatus)
