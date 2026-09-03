from app.graph import build_graph


def main():

    graph = build_graph()

    initial_state = {
        "request": "Create a learning plan for LangGraph",
        "analysis": "",
        "plan": "",
        "review": "",
        "suggestions": [],
        "approval": False,
        "revision_count": 0,
        "final_response": "",
        "error": "",
    }

    result = graph.invoke(initial_state)

    print()
    print("=" * 60)
    print("FINAL RESPONSE")
    print("=" * 60)

    print(result["final_response"])

    print()
    print("=" * 60)
    print("FINAL STATE")
    print("=" * 60)

    for key, value in result.items():
        print()
        print(f"{key}:")
        print(value)


if __name__ == "__main__":
    main()