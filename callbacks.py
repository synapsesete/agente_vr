from langchain.callbacks.base import BaseCallbackHandler


class AgentCallbackHandler(BaseCallbackHandler):

    def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        tags=None,
        metadata=None,
        **kwargs,
    ):
        print(f"***Prompt to LLM was:***\{prompts[0]}")
        print("**********")

    def on_llm_end(self, response, *, run_id, parent_run_id=None, **kwargs):
        print(f"***LLM Response:***\{response.generations[0][0].text}")
        print("**********")
