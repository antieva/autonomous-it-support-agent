from types import SimpleNamespace

from it_support_agent.agent import ITSupportAgent, TOOLS_SCHEMA


def message(content=None, tool_calls=None):
    return SimpleNamespace(content=content, tool_calls=tool_calls)


def tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **request):
        self.requests.append(request)
        return SimpleNamespace(choices=[SimpleNamespace(message=next(self.responses))])


def test_tool_result_is_attached_to_the_correct_call():
    client = FakeClient(
        [
            message(
                tool_calls=[
                    tool_call("call-1", "get_server_health", '{"server_id":"payment-server-01"}')
                ]
            ),
            message("CPU is critical; the service was restarted."),
        ]
    )

    result = ITSupportAgent(client).run("Payment server is timing out")

    assert result == "CPU is critical; the service was restarted."
    tool_message = next(item for item in client.requests[1]["messages"] if isinstance(item, dict) and item["role"] == "tool")
    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call-1"
    assert tool_message["name"] == "get_server_health"
    assert '"cpu": "98%"' in tool_message["content"]


def test_schema_contains_completed_action_parameters():
    functions = {item["function"]["name"]: item["function"] for item in TOOLS_SCHEMA}
    assert functions["restart_service"]["parameters"]["properties"]["server_id"]["type"] == "string"
    assert functions["escalate_to_engineer"]["parameters"]["properties"]["summary"]["type"] == "string"

