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

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import (
    Any,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from ondewo_nlu_webhook_server.language_code import LanguageCode


class WebhookResponseModel(BaseModel):
    fulfillmentText: str
    fulfillmentMessages: list[dict[str, Any]]
    source: str
    payload: dict[str, Any]
    outputContexts: list[dict[str, Any]]
    followupEventInput: dict[str, Any]


class TextMessage(BaseModel):
    text: list[str]


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
    parameters: dict[str, Parameter]
    lifespanTime: float | None = None

    class Config:
        # This will tell Pydantic to use the `Parameter` model for `Parameter` parsing
        # and handle nested objects automatically
        json_encoders: dict[type[Any], Callable[[Any], Any]] = {
            Parameter: lambda v: v.dict(),  # Convert Parameter object back to dict if needed
        }


class IntentMessageText(BaseModel):
    text: list[str] | None


class IntentMessageImage(BaseModel):
    image_uri: str | None
    accessibility_text: str | None


class IntentMessageQuickReplies(BaseModel):
    title: str | None
    quick_replies: list[str] | None


class IntentMessageCardButton(BaseModel):
    text: str | None
    postback: str | None


class IntentMessageCard(BaseModel):
    title: str | None
    subtitle: str | None
    image_uri: str | None
    buttons: list[IntentMessageCardButton] | None


class IntentMessageBasicCardButtonOpenUriAction(BaseModel):
    uri: str


class IntentMessageBasicCardButton(BaseModel):
    title: str
    open_uri_action: IntentMessageBasicCardButtonOpenUriAction


class IntentMessageBasicCard(BaseModel):
    title: str | None
    subtitle: str | None
    formatted_text: str | None
    image: IntentMessageImage | None
    buttons: list[IntentMessageBasicCardButton] | None


class IntentMessageSimpleResponse(BaseModel):
    text_to_speech: str | None
    ssml: str | None
    display_text: str | None


class IntentMessageSimpleResponses(BaseModel):
    simple_responses: list[IntentMessageSimpleResponse]


class IntentMessageSuggestion(BaseModel):
    title: str


class IntentMessageSuggestions(BaseModel):
    suggestions: list[IntentMessageSuggestion]


class IntentMessageLinkOutSuggestion(BaseModel):
    destination_name: str
    uri: str


class IntentMessageSelectItemInfo(BaseModel):
    key: str
    synonyms: list[str] | None


class IntentMessageCarouselSelectItem(BaseModel):
    info: IntentMessageSelectItemInfo
    title: str
    description: str | None = None
    image: IntentMessageImage | None = None


class IntentMessageCarouselSelect(BaseModel):
    items: list[IntentMessageCarouselSelectItem]


class IntentMessageListSelectItem(BaseModel):
    info: IntentMessageSelectItemInfo
    title: str
    description: str | None = None
    image: IntentMessageImage | None = None


class IntentMessageListSelect(BaseModel):
    title: str | None = None
    items: list[IntentMessageListSelectItem]


class IntentMessageHTMLText(BaseModel):
    text: list[str]


class IntentMessageVideo(BaseModel):
    uri: str | None = None
    accessibility_text: str | None = None


class IntentMessageAudio(BaseModel):
    uri: str | None = None
    accessibility_text: str | None = None


class IntentMessagePlatformEnum(StrEnum):
    PLATFORM_UNSPECIFIED = "PLATFORM_UNSPECIFIED"
    FACEBOOK = "FACEBOOK"
    SLACK = "SLACK"
    TELEGRAM = "TELEGRAM"
    KIK = "KIK"
    SKYPE = "SKYPE"
    LINE = "LINE"
    VIBER = "VIBER"
    ACTIONS_ON_GOOGLE = "ACTIONS_ON_GOOGLE"
    PLACEHOLDER_1 = "PLACEHOLDER_1"
    PLACEHOLDER_2 = "PLACEHOLDER_2"
    PLACEHOLDER_3 = "PLACEHOLDER_3"
    PLACEHOLDER_4 = "PLACEHOLDER_4"
    PLACEHOLDER_5 = "PLACEHOLDER_5"
    PLACEHOLDER_6 = "PLACEHOLDER_6"
    PLACEHOLDER_7 = "PLACEHOLDER_7"
    PLACEHOLDER_8 = "PLACEHOLDER_8"
    PLACEHOLDER_9 = "PLACEHOLDER_9"
    PLACEHOLDER_10 = "PLACEHOLDER_10"
    PLACEHOLDER_11 = "PLACEHOLDER_11"
    PLACEHOLDER_12 = "PLACEHOLDER_12"
    PLACEHOLDER_13 = "PLACEHOLDER_13"
    PLACEHOLDER_14 = "PLACEHOLDER_14"
    PLACEHOLDER_15 = "PLACEHOLDER_15"
    PLACEHOLDER_16 = "PLACEHOLDER_16"
    PLACEHOLDER_17 = "PLACEHOLDER_17"
    PLACEHOLDER_18 = "PLACEHOLDER_18"
    PLACEHOLDER_19 = "PLACEHOLDER_19"
    PLACEHOLDER_20 = "PLACEHOLDER_20"


INTENT_MESSAGE_PLATFORM_ENUM_SET: set[str] = set(IntentMessagePlatformEnum)


class IntentMessage(BaseModel):
    name: str | None = None
    language_code: str | None = None
    text: IntentMessageText | None = None
    image: IntentMessageImage | None = None
    quick_replies: IntentMessageQuickReplies | None = None
    card: IntentMessageCard | None = None
    payload: dict | None = None
    simple_responses: IntentMessageSimpleResponses | None = None
    basic_card: IntentMessageBasicCard | None = None
    suggestions: IntentMessageSuggestions | None = None
    link_out_suggestion: IntentMessageLinkOutSuggestion | None = None
    list_select: IntentMessageListSelect | None = None
    carousel_select: IntentMessageCarouselSelect | None = None
    html_text: IntentMessageHTMLText | None = None
    video: IntentMessageVideo | None = None
    audio: IntentMessageAudio | None = None
    platform: str | None = None
    is_prompt: bool | None = None

    @classmethod
    @field_validator("platform")
    def validate_platform(cls, value: str) -> str:
        if value and value not in INTENT_MESSAGE_PLATFORM_ENUM_SET:
            raise ValueError(
                f"Provided platform name '{value}' is not valid. "
                f"Platform name should be one of '{INTENT_MESSAGE_PLATFORM_ENUM_SET}'",
            )
        return value


class QueryResult(BaseModel):
    fulfillmentMessages: list[IntentMessage] | None = None
    fulfillmentText: str
    intent: Intent
    intentDetectionConfidence: float
    languageCode: str
    outputContexts: list[Context] | None = None
    parameters: dict[str, Any] | None = None
    queryText: str

    class Config:
        # This will tell Pydantic to use the `Context` model for `outputContexts` parsing
        # and handle nested objects automatically
        json_encoders: dict[type[Any], Callable[[Any], Any]] = {
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
    datastreamId: str | None = None
    identifiedUserId: str | None = None
    labels: list[str] | None = None
    originId: str | None = None
    propertyId: str | None = None
    timeZone: str | None = None


class EventInput(BaseModel):
    parameters: dict[str, Any] = Field(default_factory=dict)
    name: str | None = None
    languageCode: str | None = None


class TextInput(BaseModel):
    text: str | None = None
    languageCode: str | None = None


class InputAudioConfig(BaseModel):
    audio_encoding: str | None = None
    sample_rate_hertz: int | None = None
    language_code: str | None = None
    phrase_hints: list[str] | None = None


class DocumentFileResource(BaseModel):
    name: str | None = None
    display_name: str | None = None
    data: bytes | None = None


class AudioFileResource(BaseModel):
    name: str | None = None
    data: bytes | None = None
    language: str | None = None
    duration_in_s: float | None = None
    sample_rate: int | None = None
    audio_file_resource_type: str | None = None
    transcriptions: list[dict] | None = None


class ImageFileResource(BaseModel):
    name: str | None = None
    display_name: str | None = None
    data: bytes | None = None


class VideoFileResource(BaseModel):
    name: str | None = None
    display_name: str | None = None
    data: bytes | None = None
    duration_in_s: float | None = None
    resolution: str | None = None
    frame_rate: float | None = None


class FileResources(BaseModel):
    document_file_resource: DocumentFileResource | None = None
    audio_file_resource: AudioFileResource | None = None
    image_file_resource: ImageFileResource | None = None
    video_file_resource: VideoFileResource | None = None


class QueryInput(BaseModel):
    text: TextInput | None = None
    audio_config: InputAudioConfig | None = None
    event: EventInput | None = None
    file_resources: list[FileResources] | None = None


class Payload(BaseModel):
    queryInput: QueryInput
    queryParams: QueryParams
    session: str


class OriginalDetectIntentRequest(BaseModel):
    payload: Payload  # Include the payload as a nested class


class GetIntentRequest(BaseModel):
    name: str
    languageCode: str | None = ""


class LoginRequest(BaseModel):
    userEmail: str
    password: str


class LoginResponse(BaseModel):
    user: Any
    authToken: str


class WebhookResponse(BaseModel):
    fulfillmentText: str
    fulfillmentMessages: list[IntentMessage]
    source: str
    payload: dict[str, Any]
    outputContexts: list[Context] | None
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

    headers: dict[str, str] | None = Field(default_factory=dict)  # type: ignore
    detectIntentRequest: OriginalDetectIntentRequest
    queryResult: QueryResult
    responseId: str
    session: str

    @classmethod
    def create_sample_request(cls, language_code: LanguageCode = LanguageCode.en_US) -> WebhookRequest:
        language_code_str: str = language_code.value
        return cls(
            responseId="testID",
            queryResult=QueryResult(
                queryText="This is a question",
                parameters={},
                fulfillmentText="",
                fulfillmentMessages=[
                    IntentMessage(
                        text=IntentMessageText(
                            text=[
                                "first message",
                                "second message",
                            ],
                        ),
                        platform=IntentMessagePlatformEnum.PLATFORM_UNSPECIFIED.value,
                    ),
                ],
                outputContexts=[
                    Context(
                        name="context name 1",
                        lifespanCount=1,
                        parameters={
                            "parameter1": Parameter(value="1", value_original="1", display_name="1", name=""),
                            "parameter2": Parameter(value="2", value_original="2", display_name="2", name=""),
                        },
                    ),
                    Context(
                        name="context name 2",
                        lifespanCount=1,
                        parameters={
                            "parameter1": Parameter(value="1", value_original="1", display_name="1", name=""),
                        },
                    ),
                ],
                intent=Intent(
                    name="projects/<PROJECT-ID>/sessions/<SESSION-ID>/agent/intents/<INTENT-ID>",
                    displayName="some intent name",
                ),
                intentDetectionConfidence=99,
                languageCode=language_code_str,
            ),
            detectIntentRequest=OriginalDetectIntentRequest(
                payload=Payload(
                    queryInput=QueryInput(
                        text=TextInput(
                            languageCode=language_code_str,
                            text="This is a question",
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
                    session="projects/<PROJECT-ID>/sessions/<SESSION-ID>",
                ),
            ),
            # Ensure 'payload' field is provided
            session="/path/of/session",
            headers={
                "header1": "value1",
            },
        )
