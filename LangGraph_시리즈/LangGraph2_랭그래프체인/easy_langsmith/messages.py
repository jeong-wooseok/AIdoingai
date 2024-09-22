from langchain_core.messages import AIMessageChunk


def stream_response(response, return_output=False):
"""
Streams responses from an AI model, processing and outputting each chunk.

This function iterates over each item in the `response` iterable. If the item is an instance of `AIMessageChunk`,
it extracts the content of the chunk and outputs it. If the item is a string, it outputs the string directly.
Optionally, the function can return the concatenated string of all response chunks.

Parameters:
- response (iterable): An iterable of response chunks, which can be `AIMessageChunk` objects or strings
- return_output (bool, optional): If True, returns the concatenated response string as a string

Returns:
- str: If `return_output` is True, the concatenated response string. If False, nothing is returned.
"""
    answer = ""
    for token in response:
        if isinstance(token, AIMessageChunk):
            answer += token.content
            print(token.content, end="", flush=True)
        elif isinstance(token, str):
            answer += token
            print(token, end="", flush=True)
    if return_output:
        return answer
