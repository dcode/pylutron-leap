from pylutron_leap.api.emergency import EmergencyStatus, LeapEmergencyBody
from pylutron_leap.api.enum import (
    CommuniqueType,
    EmergencyStateEnum,
    MessageBodyTypeEnum,
)
from pylutron_leap.api.message import (
    LeapDirectives,
    LeapExceptionBody,
    LeapMessage,
    LeapMessageHeader,
    ResponseStatus,
)


def test_leapheader_schema():
    _EXPECTED_DICT: dict[str, str] = {"Url": "/server/status/ping"}
    _EXPECTED_OBJ: LeapMessageHeader = LeapMessageHeader(Url="/server/status/ping")

    _dict = LeapMessageHeader.Schema().dump(_EXPECTED_OBJ)
    assert _dict == _EXPECTED_DICT

    _obj = LeapMessageHeader.Schema().load(_EXPECTED_DICT)
    assert isinstance(_obj, LeapMessageHeader)
    assert _obj.ClientTag is None

    _EXPECTED_DICT: dict[str, str] = {
        "StatusCode": "200 OK",
        "ClientTag": "c66a3051-5355-497f-8958-02f9fb2c607d",
        "Url": "/not/a/real/endpoint",
        "MessageBodyType": "OneAreaStatus",
        "Directives": {"SuppressMessageBody": False},
    }

    _EXPECTED_OBJ: LeapMessageHeader = LeapMessageHeader(
        Url="/not/a/real/endpoint",
        StatusCode=ResponseStatus(code=200, message="OK"),
        ClientTag="c66a3051-5355-497f-8958-02f9fb2c607d",
        MessageBodyType=MessageBodyTypeEnum.OneAreaStatus,
        Directives=LeapDirectives(SuppressMessageBody=False),
    )
    _dict = LeapMessageHeader.Schema().dump(_EXPECTED_OBJ)

    assert _dict == _EXPECTED_DICT
    assert _dict["Directives"]["SuppressMessageBody"] is False

    _obj = LeapMessageHeader.Schema().load(_EXPECTED_DICT)
    assert _obj.StatusCode.is_successful() is True
    assert _obj == _EXPECTED_OBJ
    assert _obj.ClientTag == "c66a3051-5355-497f-8958-02f9fb2c607d"


def test_leapmessagebase_schema():
    _EXPECTED_DICT: dict = {
        "CommuniqueType": "ReadRequest",
        "Header": {"Url": "/server/status/ping"},
    }

    _EXPECTED_OBJ = LeapMessage(
        CommuniqueType=CommuniqueType.ReadRequest,
        Header=LeapMessageHeader(Url="/server/status/ping"),
    )
    _dict = LeapMessage.Schema().dump(_EXPECTED_OBJ)

    assert _dict == _EXPECTED_DICT


def test_leapexceptionmessage_schema():
    _EXPECTED_DICT: dict = {
        "CommuniqueType": "ReadResponse",
        "Header": {"Url": "/not/a/real/url"},
        "Body": {"Message": "Something went wrong"},
    }

    _EXCPECTED_OBJ: LeapMessage = LeapMessage(
        CommuniqueType=CommuniqueType.ReadResponse,
        Header=LeapMessageHeader(Url="/not/a/real/url"),
        Body=LeapExceptionBody(Message="Something went wrong"),
    )

    print(_EXCPECTED_OBJ.__dict__)
    _dict = LeapMessage.Schema().dump(_EXCPECTED_OBJ)

    assert _dict == _EXPECTED_DICT


def test_emergencymessage_schema():
    _EXPECTED_DICT: dict = {
        "CommuniqueType": "UpdateRequest",
        "Header": {"Url": "/emergency/flash/status"},
        "Body": {"EmergencyStatus": {"ActiveState": "Active"}},
    }

    _EXPECTED_OBJ = LeapMessage(
        CommuniqueType=CommuniqueType.UpdateRequest,
        Header=LeapMessageHeader(Url="/emergency/flash/status"),
        Body=LeapEmergencyBody(
            EmergencyStatus=EmergencyStatus(ActiveState=EmergencyStateEnum.Active)
        ),
    )

    _dict = LeapMessage.Schema().dump(_EXPECTED_OBJ)

    assert _dict == _EXPECTED_DICT

    _obj = LeapMessage.Schema().load(_EXPECTED_DICT)

    assert _obj == _EXPECTED_OBJ
