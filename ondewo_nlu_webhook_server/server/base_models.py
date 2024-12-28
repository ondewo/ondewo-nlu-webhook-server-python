# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Definitions of json dataclass objects used for communication from & to the webhook server
"""
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from ondewo_nlu_webhook_server.language_code import LanguageCode


class WebhookResponseModel(BaseModel):
    fulfillmentText: str
    fulfillmentMessages: list[Dict[str, Any]]
    source: str
    payload: Dict[str, Any]
    outputContexts: list[Dict[str, Any]]
    followupEventInput: Dict[str, Any]


class TextMessage(BaseModel):
    text: List[str]


class FulfillmentMessage(BaseModel):
    text: TextMessage


class Intent(BaseModel):
    name: str
    displayName: str


class Parameter(BaseModel):
    name: str
    display_name: str
    value: str
    value_original: str


class Context(BaseModel):
    name: str
    lifespanCount: int
    parameters: Dict[str, Parameter]
    lifespanTime: Optional[float] = None

    class Config:
        # This will tell Pydantic to use the `Parameter` model for `Parameter` parsing
        # and handle nested objects automatically
        json_encoders: Dict[Type[Any], Callable[[Any], Any]] = {
            Parameter: lambda v: v.dict(),  # Convert Parameter object back to dict if needed
        }


class IntentMessageText(BaseModel):
    text: Optional[List[str]]


class IntentMessageImage(BaseModel):
    image_uri: Optional[str]
    accessibility_text: Optional[str]


class IntentMessageQuickReplies(BaseModel):
    title: Optional[str]
    quick_replies: Optional[List[str]]


class IntentMessageCardButton(BaseModel):
    text: Optional[str]
    postback: Optional[str]


class IntentMessageCard(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    image_uri: Optional[str]
    buttons: Optional[List[IntentMessageCardButton]]


class IntentMessageBasicCardButtonOpenUriAction(BaseModel):
    uri: str


class IntentMessageBasicCardButton(BaseModel):
    title: str
    open_uri_action: IntentMessageBasicCardButtonOpenUriAction


class IntentMessageBasicCard(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    formatted_text: Optional[str]
    image: Optional[IntentMessageImage]
    buttons: Optional[List[IntentMessageBasicCardButton]]


class IntentMessageSimpleResponse(BaseModel):
    text_to_speech: Optional[str]
    ssml: Optional[str]
    display_text: Optional[str]


class IntentMessageSimpleResponses(BaseModel):
    simple_responses: List[IntentMessageSimpleResponse]


class IntentMessageSuggestion(BaseModel):
    title: str


class IntentMessageSuggestions(BaseModel):
    suggestions: List[IntentMessageSuggestion]


class IntentMessageLinkOutSuggestion(BaseModel):
    destination_name: str
    uri: str


class IntentMessageSelectItemInfo(BaseModel):
    key: str
    synonyms: Optional[List[str]]


class IntentMessageCarouselSelectItem(BaseModel):
    info: IntentMessageSelectItemInfo
    title: str
    description: Optional[str] = None
    image: Optional[IntentMessageImage] = None


class IntentMessageCarouselSelect(BaseModel):
    items: List[IntentMessageCarouselSelectItem]


class IntentMessageListSelectItem(BaseModel):
    info: IntentMessageSelectItemInfo
    title: str
    description: Optional[str] = None
    image: Optional[IntentMessageImage] = None


class IntentMessageListSelect(BaseModel):
    title: Optional[str] = None
    items: List[IntentMessageListSelectItem]


class IntentMessageHTMLText(BaseModel):
    text: List[str]


class IntentMessageVideo(BaseModel):
    uri: Optional[str] = None
    accessibility_text: Optional[str] = None


class IntentMessageAudio(BaseModel):
    uri: Optional[str] = None
    accessibility_text: Optional[str] = None


class IntentMessagePlatformEnum(str, Enum):
    PLATFORM_UNSPECIFIED = 'PLATFORM_UNSPECIFIED'
    FACEBOOK = 'FACEBOOK'
    SLACK = 'SLACK'
    TELEGRAM = 'TELEGRAM'
    KIK = 'KIK'
    SKYPE = 'SKYPE'
    LINE = 'LINE'
    VIBER = 'VIBER'
    ACTIONS_ON_GOOGLE = 'ACTIONS_ON_GOOGLE'
    PLACEHOLDER_1 = 'PLACEHOLDER_1'
    PLACEHOLDER_2 = 'PLACEHOLDER_2'
    PLACEHOLDER_3 = 'PLACEHOLDER_3'
    PLACEHOLDER_4 = 'PLACEHOLDER_4'
    PLACEHOLDER_5 = 'PLACEHOLDER_5'
    PLACEHOLDER_6 = 'PLACEHOLDER_6'
    PLACEHOLDER_7 = 'PLACEHOLDER_7'
    PLACEHOLDER_8 = 'PLACEHOLDER_8'
    PLACEHOLDER_9 = 'PLACEHOLDER_9'
    PLACEHOLDER_10 = 'PLACEHOLDER_10'
    PLACEHOLDER_11 = 'PLACEHOLDER_11'
    PLACEHOLDER_12 = 'PLACEHOLDER_12'
    PLACEHOLDER_13 = 'PLACEHOLDER_13'
    PLACEHOLDER_14 = 'PLACEHOLDER_14'
    PLACEHOLDER_15 = 'PLACEHOLDER_15'
    PLACEHOLDER_16 = 'PLACEHOLDER_16'
    PLACEHOLDER_17 = 'PLACEHOLDER_17'
    PLACEHOLDER_18 = 'PLACEHOLDER_18'
    PLACEHOLDER_19 = 'PLACEHOLDER_19'
    PLACEHOLDER_20 = 'PLACEHOLDER_20'


INTENT_MESSAGE_PLATFORM_ENUM_SET: Set[str] = {enum_type for enum_type in IntentMessagePlatformEnum}


class IntentMessage(BaseModel):
    name: Optional[str] = None
    language_code: Optional[str] = None
    text: Optional[IntentMessageText] = None
    image: Optional[IntentMessageImage] = None
    quick_replies: Optional[IntentMessageQuickReplies] = None
    card: Optional[IntentMessageCard] = None
    payload: Optional[dict] = None
    simple_responses: Optional[IntentMessageSimpleResponses] = None
    basic_card: Optional[IntentMessageBasicCard] = None
    suggestions: Optional[IntentMessageSuggestions] = None
    link_out_suggestion: Optional[IntentMessageLinkOutSuggestion] = None
    list_select: Optional[IntentMessageListSelect] = None
    carousel_select: Optional[IntentMessageCarouselSelect] = None
    html_text: Optional[IntentMessageHTMLText] = None
    video: Optional[IntentMessageVideo] = None
    audio: Optional[IntentMessageAudio] = None
    platform: Optional[str] = None
    is_prompt: Optional[bool] = None

    @classmethod
    @field_validator('platform')
    def validate_platform(cls, value: str) -> str:
        if value and value not in INTENT_MESSAGE_PLATFORM_ENUM_SET:
            raise ValueError(
                f"Provided platform name '{value}' is not valid. "
                f"Platform name should be one of '{INTENT_MESSAGE_PLATFORM_ENUM_SET}'",
            )
        return value


class QueryResult(BaseModel):
    fulfillmentMessages: Optional[List[IntentMessage]] = None
    fulfillmentText: str
    intent: Intent
    intentDetectionConfidence: float
    languageCode: str
    outputContexts: Optional[List[Context]] = None
    parameters: Optional[Dict[str, Any]] = None
    queryText: str

    class Config:
        # This will tell Pydantic to use the `Context` model for `outputContexts` parsing
        # and handle nested objects automatically
        json_encoders: Dict[Type[Any], Callable[[Any], Any]] = {
            Context: lambda v: v.dict(),  # Convert Context object back to dict if needed
            IntentMessage: lambda v: v.dict(),
            IntentMessageText: lambda v: v.dict(),
            IntentMessageImage: lambda v: v.dict(),
            IntentMessageQuickReplies: lambda v: v.dict(),
            IntentMessageCard: lambda v: v.dict(),
            IntentMessageCardButton: lambda v: v.dict(),
            IntentMessageBasicCardButtonOpenUriAction: lambda v: v.dict(),
            IntentMessageBasicCardButton: lambda v: v.dict(),
            IntentMessageBasicCard: lambda v: v.dict(),
            IntentMessageSimpleResponse: lambda v: v.dict(),
            IntentMessageSimpleResponses: lambda v: v.dict(),
            IntentMessageSuggestion: lambda v: v.dict(),
            IntentMessageSuggestions: lambda v: v.dict(),
            IntentMessageLinkOutSuggestion: lambda v: v.dict(),
            IntentMessageSelectItemInfo: lambda v: v.dict(),
            IntentMessageCarouselSelectItem: lambda v: v.dict(),
            IntentMessageCarouselSelect: lambda v: v.dict(),
            IntentMessageListSelectItem: lambda v: v.dict(),
            IntentMessageListSelect: lambda v: v.dict(),
            IntentMessageHTMLText: lambda v: v.dict(),
            IntentMessageVideo: lambda v: v.dict(),
            IntentMessageAudio: lambda v: v.dict(),
        }


class QueryParams(BaseModel):
    datastreamId: Optional[str] = None
    identifiedUserId: Optional[str] = None
    labels: Optional[List[str]] = None
    originId: Optional[str] = None
    propertyId: Optional[str] = None
    timeZone: Optional[str] = None


class EventInput(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    name: Optional[str] = None
    languageCode: Optional[str] = None


class TextInput(BaseModel):
    text: Optional[str] = None
    languageCode: Optional[str] = None


class InputAudioConfig(BaseModel):
    audio_encoding: Optional[str] = None
    sample_rate_hertz: Optional[int] = None
    language_code: Optional[str] = None
    phrase_hints: Optional[List[str]] = None


class DocumentFileResource(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    bytes: Optional[bytes] = None


class AudioFileResource(BaseModel):
    name: Optional[str] = None
    bytes: Optional[bytes] = None
    language: Optional[str] = None
    duration_in_s: Optional[float] = None
    sample_rate: Optional[int] = None
    audio_file_resource_type: Optional[str] = None
    transcriptions: Optional[List[dict]] = None


class ImageFileResource(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    bytes: Optional[bytes] = None


class VideoFileResource(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    bytes: Optional[bytes] = None
    duration_in_s: Optional[float] = None
    resolution: Optional[str] = None
    frame_rate: Optional[float] = None


class FileResources(BaseModel):
    document_file_resource: Optional[DocumentFileResource] = None
    audio_file_resource: Optional[AudioFileResource] = None
    image_file_resource: Optional[ImageFileResource] = None
    video_file_resource: Optional[VideoFileResource] = None


class QueryInput(BaseModel):
    text: Optional[TextInput] = None
    audio_config: Optional[InputAudioConfig] = None
    event: Optional[EventInput] = None
    file_resources: Optional[List[FileResources]] = None


class Payload(BaseModel):
    queryInput: QueryInput
    queryParams: QueryParams
    session: str


class OriginalDetectIntentRequest(BaseModel):
    payload: Payload  # Include the payload as a nested class


class GetIntentRequest(BaseModel):
    name: str
    languageCode: Optional[str] = ""


class LoginRequest(BaseModel):
    userEmail: str
    password: str


class LoginResponse(BaseModel):
    user: Any
    authToken: str


class WebhookResponse(BaseModel):
    fulfillmentText: str
    fulfillmentMessages: List[IntentMessage]
    source: str
    payload: Dict[str, Any]
    outputContexts: Optional[List[Context]]
    followupEventInput: EventInput  # TODO: make better so pydantic can parse full objects according to proto
    """
    webhook response json dataclass for communication from the webhook server to ondewo-cai
    provides a static .validate() method to validate format of json formatted dictionary

    Attributes:
        fulfillment_text        # (unused by ondewo-cai)
        fulfillment_messages    # list of response messages for detected intent
        source                  # string passed directly to QueryResult.webhook_source of ondewo-cai
        payload                 # payload dictionary passed directly to QueryResult.webhook_payload of ondewo-cai
        output_contexts         # list of active active_contexts
        followup_event_input    # (unused atm)
    """

    # @staticmethod
    # def validate(dic: Union[dict, 'WebhookResponse']) -> bool:
    #     if isinstance(dic, WebhookResponse):
    #         dic = dic.dict()
    #     try:
    #         j_validate(instance=dic, schema=response_schema)
    #         return True
    #     except ValidationError:
    #         return False


class WebhookRequest(BaseModel):
    """
    request json dataclass for communication from ondewo-cai to the webhook server
    provides a static .validate() method to validate format of json formatted dictionary

    attributes:
        responseId                             # ID of response
        queryResult                            # Information about the current state of the query
            queryResult.queryText              # Query text matched to the intent
            queryResult.parameters             # dict, global parameters and their values
            queryResult.fulfillmentText        # current fulfillment text
            queryResult.fulfillmentMessages    # collection of response messages for detected intent
            queryResult.outputContexts         # list of active_contexts
                queryResult.outputContexts[0]  # first active context, each context has a .name, .lifespanCount and
                                               # .parameters attribute
                queryResult.outputContexts[0].parameters
                                               # dict, parameters for this context, related [parameter name]:[parameter
                                               # value]
            queryResult.intent                 # matched intent, has a .name and .displayName attribute
            queryResult.intentDetectionConfidence
                                               # numeric value for confidence of intent detection
            queryResult.languageCode           # str code for language (e.g. 'en', 'de')
        originalDetectIntentRequest            #
        session                                # session ID
        headers                                # optional, list of headers sent with the request
    """
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)  # type:ignore
    detectIntentRequest: OriginalDetectIntentRequest
    queryResult: QueryResult
    responseId: str
    session: str

    @classmethod
    def create_sample_request(cls, language_code: LanguageCode = LanguageCode.en_US) -> 'WebhookRequest':
        language_code_str: str = language_code.value
        return cls(
            responseId='testID',
            queryResult=QueryResult(
                queryText='This is a question',
                parameters={},
                fulfillmentText='',
                fulfillmentMessages=[
                    IntentMessage(
                        text=IntentMessageText(
                            text=[
                                'first message',
                                'second message',
                            ],
                        ),
                        platform=IntentMessagePlatformEnum.PLATFORM_UNSPECIFIED.value,
                    ),
                ],
                outputContexts=[
                    Context(
                        name='context name 1',
                        lifespanCount=1,
                        parameters={
                            'parameter1': Parameter(value='1', value_original='1', display_name='1', name=''),
                            'parameter2': Parameter(value='2', value_original='2', display_name='2', name=''),
                        },
                    ),
                    Context(
                        name='context name 2',
                        lifespanCount=1,
                        parameters={
                            'parameter1': Parameter(value='1', value_original='1', display_name='1', name=''),
                        },
                    ),
                ],
                intent=Intent(
                    name='projects/<PROJECT-ID>/sessions/<SESSION-ID>/agent/intents/<INTENT-ID>',
                    displayName='some intent name',
                ),
                intentDetectionConfidence=99,
                languageCode=language_code_str,
            ),
            detectIntentRequest=OriginalDetectIntentRequest(
                payload=Payload(
                    queryInput=QueryInput(
                        text=TextInput(
                            languageCode=language_code_str,
                            text='This is a question',
                        ),
                    ),
                    queryParams=QueryParams(
                        datastreamId=None,
                        identifiedUserId=None,
                        labels=None,
                        originId=None,
                        propertyId=None,
                        timeZone=None,
                    ),
                    session='projects/<PROJECT-ID>/sessions/<SESSION-ID>',
                ),
            ),
            # Ensure 'payload' field is provided
            session='/path/of/session',
            headers={
                'header1': 'value1',
            },
        )
