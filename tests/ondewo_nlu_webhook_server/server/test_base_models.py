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

import pytest
from pydantic_core import ValidationError

from ondewo_nlu_webhook_server.language_code import LanguageCode
from ondewo_nlu_webhook_server.server.base_models import (
    INTENT_MESSAGE_PLATFORM_ENUM_SET,
    IntentMessage,
    IntentMessageAudio,
    IntentMessageBasicCard,
    IntentMessageBasicCardButton,
    IntentMessageBasicCardButtonOpenUriAction,
    IntentMessageCard,
    IntentMessageCardButton,
    IntentMessageCarouselSelect,
    IntentMessageCarouselSelectItem,
    IntentMessageHTMLText,
    IntentMessageImage,
    IntentMessageLinkOutSuggestion,
    IntentMessageListSelect,
    IntentMessageListSelectItem,
    IntentMessagePlatformEnum,
    IntentMessageQuickReplies,
    IntentMessageSelectItemInfo,
    IntentMessageSimpleResponse,
    IntentMessageSimpleResponses,
    IntentMessageSuggestion,
    IntentMessageSuggestions,
    IntentMessageText,
    IntentMessageVideo,
    WebhookRequest,
)


class TestIntentMessageValidatePlatform:
    """Tests for IntentMessage.validate_platform field validator."""

    def test_valid_platform_platform_unspecified(self) -> None:
        """IntentMessage with PLATFORM_UNSPECIFIED should be created successfully."""
        msg = IntentMessage(platform="PLATFORM_UNSPECIFIED")
        assert msg.platform == "PLATFORM_UNSPECIFIED"

    def test_valid_platform_facebook(self) -> None:
        """IntentMessage with FACEBOOK platform should be created successfully."""
        msg = IntentMessage(platform="FACEBOOK")
        assert msg.platform == "FACEBOOK"

    def test_valid_platform_slack(self) -> None:
        """IntentMessage with SLACK platform should be created successfully."""
        msg = IntentMessage(platform="SLACK")
        assert msg.platform == "SLACK"

    def test_valid_platform_telegram(self) -> None:
        """IntentMessage with TELEGRAM platform should be created successfully."""
        msg = IntentMessage(platform="TELEGRAM")
        assert msg.platform == "TELEGRAM"

    def test_valid_platform_actions_on_google(self) -> None:
        """IntentMessage with ACTIONS_ON_GOOGLE platform should be created successfully."""
        msg = IntentMessage(platform="ACTIONS_ON_GOOGLE")
        assert msg.platform == "ACTIONS_ON_GOOGLE"

    def test_platform_none_is_allowed(self) -> None:
        """IntentMessage with platform=None should be created successfully and return None."""
        msg = IntentMessage(platform=None)
        assert msg.platform is None

    def test_platform_not_provided_defaults_to_none(self) -> None:
        """IntentMessage without platform field should default to None."""
        msg = IntentMessage()
        assert msg.platform is None

    def test_invalid_platform_raises_validation_error(self) -> None:
        """IntentMessage with an invalid platform should raise ValidationError."""
        with pytest.raises(ValidationError):
            IntentMessage(platform="INVALID_PLATFORM")

    def test_invalid_platform_error_message_contains_value(self) -> None:
        """ValidationError for invalid platform should mention the bad value."""
        with pytest.raises(ValidationError) as exc_info:
            IntentMessage(platform="TOTALLY_WRONG")
        error_str = str(exc_info.value)
        assert "TOTALLY_WRONG" in error_str

    def test_invalid_platform_random_string_raises_validation_error(self) -> None:
        """Any arbitrary string not in the enum should raise ValidationError."""
        with pytest.raises(ValidationError):
            IntentMessage(platform="not_a_valid_platform_123")

    def test_all_enum_values_are_valid(self) -> None:
        """Every value in IntentMessagePlatformEnum should be accepted without error."""
        for platform_value in IntentMessagePlatformEnum:
            msg = IntentMessage(platform=platform_value.value)
            assert msg.platform == platform_value.value

    def test_intent_message_platform_enum_set_is_populated(self) -> None:
        """INTENT_MESSAGE_PLATFORM_ENUM_SET should contain all enum members."""
        assert len(INTENT_MESSAGE_PLATFORM_ENUM_SET) == len(IntentMessagePlatformEnum)
        for platform_value in IntentMessagePlatformEnum:
            assert platform_value.value in INTENT_MESSAGE_PLATFORM_ENUM_SET


class TestWebhookRequestCreateSampleRequest:
    """Tests for WebhookRequest.create_sample_request class method."""

    def test_create_sample_request_returns_webhook_request(self) -> None:
        """create_sample_request should return a valid WebhookRequest instance."""
        request = WebhookRequest.create_sample_request()
        assert isinstance(request, WebhookRequest)

    def test_create_sample_request_default_language_code(self) -> None:
        """create_sample_request with default language code should use en_US."""
        request = WebhookRequest.create_sample_request()
        assert request.queryResult.languageCode == LanguageCode.en_US.value

    def test_create_sample_request_custom_language_code(self) -> None:
        """create_sample_request should accept a custom language code."""
        request = WebhookRequest.create_sample_request(language_code=LanguageCode.de_DE)
        assert request.queryResult.languageCode == LanguageCode.de_DE.value

    def test_create_sample_request_has_response_id(self) -> None:
        """create_sample_request should include a responseId."""
        request = WebhookRequest.create_sample_request()
        assert request.responseId == "testID"

    def test_create_sample_request_has_fulfillment_messages(self) -> None:
        """create_sample_request should include at least one fulfillmentMessage."""
        request = WebhookRequest.create_sample_request()
        assert request.queryResult.fulfillmentMessages
        assert len(request.queryResult.fulfillmentMessages) >= 1

    def test_create_sample_request_message_has_valid_platform(self) -> None:
        """The fulfillmentMessage in the sample request should have a valid platform."""
        request = WebhookRequest.create_sample_request()
        messages = request.queryResult.fulfillmentMessages
        assert messages is not None
        for msg in messages:
            if msg.platform is not None:
                assert msg.platform in INTENT_MESSAGE_PLATFORM_ENUM_SET

    def test_create_sample_request_has_output_contexts(self) -> None:
        """create_sample_request should include output contexts."""
        request = WebhookRequest.create_sample_request()
        assert request.queryResult.outputContexts
        assert len(request.queryResult.outputContexts) == 2

    def test_create_sample_request_has_headers(self) -> None:
        """create_sample_request should include headers."""
        request = WebhookRequest.create_sample_request()
        assert request.headers == {"header1": "value1"}


class TestIntentMessageInstantiation:
    """Tests for instantiating IntentMessage with various optional fields."""

    def test_intent_message_with_text(self) -> None:
        """IntentMessage with a text field should be created successfully."""
        msg = IntentMessage(text=IntentMessageText(text=["hello", "world"]))
        assert msg.text is not None
        assert msg.text.text == ["hello", "world"]

    def test_intent_message_with_image(self) -> None:
        """IntentMessage with an image field should be created successfully."""
        msg = IntentMessage(
            image=IntentMessageImage(image_uri="http://example.com/img.png", accessibility_text="an image"),
        )
        assert msg.image is not None
        assert msg.image.image_uri == "http://example.com/img.png"

    def test_intent_message_with_quick_replies(self) -> None:
        """IntentMessage with quick_replies should be created successfully."""
        msg = IntentMessage(quick_replies=IntentMessageQuickReplies(title="Pick one", quick_replies=["Yes", "No"]))
        assert msg.quick_replies is not None
        assert "Yes" in msg.quick_replies.quick_replies

    def test_intent_message_with_card(self) -> None:
        """IntentMessage with a card should be created successfully."""
        msg = IntentMessage(
            card=IntentMessageCard(
                title="Card Title",
                subtitle="Card Subtitle",
                image_uri="http://example.com/card.png",
                buttons=[IntentMessageCardButton(text="Click me", postback="postback_value")],
            ),
        )
        assert msg.card is not None
        assert msg.card.title == "Card Title"

    def test_intent_message_with_payload(self) -> None:
        """IntentMessage with a payload dict should be created successfully."""
        msg = IntentMessage(payload={"key": "value", "num": 42})
        assert msg.payload == {"key": "value", "num": 42}

    def test_intent_message_with_simple_responses(self) -> None:
        """IntentMessage with simple_responses should be created successfully."""
        msg = IntentMessage(
            simple_responses=IntentMessageSimpleResponses(
                simple_responses=[IntentMessageSimpleResponse(text_to_speech="Hello", ssml=None, display_text="Hello")],
            ),
        )
        assert msg.simple_responses is not None

    def test_intent_message_with_suggestions(self) -> None:
        """IntentMessage with suggestions should be created successfully."""
        msg = IntentMessage(
            suggestions=IntentMessageSuggestions(suggestions=[IntentMessageSuggestion(title="Option A")]),
        )
        assert msg.suggestions is not None
        assert msg.suggestions.suggestions[0].title == "Option A"

    def test_intent_message_with_link_out_suggestion(self) -> None:
        """IntentMessage with link_out_suggestion should be created successfully."""
        msg = IntentMessage(
            link_out_suggestion=IntentMessageLinkOutSuggestion(destination_name="Example", uri="http://example.com"),
        )
        assert msg.link_out_suggestion is not None

    def test_intent_message_with_html_text(self) -> None:
        """IntentMessage with html_text should be created successfully."""
        msg = IntentMessage(html_text=IntentMessageHTMLText(text=["<p>Hello</p>"]))
        assert msg.html_text is not None
        assert "<p>Hello</p>" in msg.html_text.text

    def test_intent_message_with_video(self) -> None:
        """IntentMessage with video should be created successfully."""
        msg = IntentMessage(video=IntentMessageVideo(uri="http://example.com/video.mp4", accessibility_text="a video"))
        assert msg.video is not None
        assert msg.video.uri == "http://example.com/video.mp4"

    def test_intent_message_with_audio(self) -> None:
        """IntentMessage with audio should be created successfully."""
        msg = IntentMessage(
            audio=IntentMessageAudio(uri="http://example.com/audio.mp3", accessibility_text="audio clip"),
        )
        assert msg.audio is not None
        assert msg.audio.uri == "http://example.com/audio.mp3"

    def test_intent_message_is_prompt_field(self) -> None:
        """IntentMessage with is_prompt=True should be created successfully."""
        msg = IntentMessage(is_prompt=True)
        assert msg.is_prompt is True

    def test_intent_message_with_list_select(self) -> None:
        """IntentMessage with list_select should be created successfully."""
        msg = IntentMessage(
            list_select=IntentMessageListSelect(
                title="Pick an item",
                items=[
                    IntentMessageListSelectItem(
                        info=IntentMessageSelectItemInfo(key="item1", synonyms=["one", "first"]),
                        title="Item 1",
                    ),
                ],
            ),
        )
        assert msg.list_select is not None
        assert msg.list_select.title == "Pick an item"

    def test_intent_message_with_carousel_select(self) -> None:
        """IntentMessage with carousel_select should be created successfully."""
        msg = IntentMessage(
            carousel_select=IntentMessageCarouselSelect(
                items=[
                    IntentMessageCarouselSelectItem(
                        info=IntentMessageSelectItemInfo(key="carousel1", synonyms=None),
                        title="Carousel Item",
                    ),
                ],
            ),
        )
        assert msg.carousel_select is not None

    def test_intent_message_with_basic_card(self) -> None:
        """IntentMessage with basic_card should be created successfully."""
        msg = IntentMessage(
            basic_card=IntentMessageBasicCard(
                title="Basic Card",
                subtitle="Subtitle",
                formatted_text="Some text",
                image=None,
                buttons=[
                    IntentMessageBasicCardButton(
                        title="Open",
                        open_uri_action=IntentMessageBasicCardButtonOpenUriAction(uri="http://example.com"),
                    ),
                ],
            ),
        )
        assert msg.basic_card is not None
        assert msg.basic_card.title == "Basic Card"
