import os


def langsmith(project_name=None, set_enable=True):

    if set_enable:
        result = os.environ.get("LANGCHAIN_API_KEY")
        if result is None or result.strip() == "":
            print(
                "LangChain API Key is not activated. refered: https://wikidocs.net/250954"
            )
            return
        os.environ["LANGCHAIN_ENDPOINT"] = (
            "https://api.smith.langchain.com"  # LangSmith API endpoint
        )
        os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: activated
        os.environ["LANGCHAIN_PROJECT"] = project_name  # project name
        print(f"LangSmith logging start\n[Project]\n{project_name}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"  # false: inactivated
        print("LangSmith logging finished")


def env_variable(key, value):
    os.environ[key] = value
