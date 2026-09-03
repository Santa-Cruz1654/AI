from app.state import State


def print_state(label: str, state: State) -> None:
    """
    Print the complete current workflow state.
    """

    print()
    print("=" * 60)
    print(label)
    print("=" * 60)

    print(f"request:        {state.get('request', '')}")
    print(f"analysis:       {state.get('analysis', '')}")
    print(f"plan:           {state.get('plan', '')}")
    print(f"review:         {state.get('review', '')}")
    print(f"approval:       {state.get('approval', False)}")
    print(f"revision_count: {state.get('revision_count', 0)}")
    print(f"final_response: {state.get('final_response', '')}")
    print(f"error:          {state.get('error', '')}")


def print_update(node_name: str, update: dict) -> None:
    """
    Print the state update returned by a node.
    """

    print()
    print(f"STATE UPDATE FROM {node_name.upper()}:")
    print(update)


def print_router_decision(
    router_name: str,
    decision: str,
) -> None:
    """
    Print the routing decision made after a node.
    """

    print()
    print("=" * 60)
    print(f"ROUTER: {router_name}")
    print("=" * 60)

    print(f"Decision: {decision}")