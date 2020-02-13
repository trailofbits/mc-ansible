from state_pb2 import State


def format_state(state):
    if state.type == State.READY:
        return f"State {state.id}"
    elif state.type == State.BUSY:
        return f"State {state.id} ({state.num_executing} ins)"
    elif state.type == State.TERMINATED:
        return f"State {state.id} ({state.reason})"
    elif state.type == State.KILLED:
        return f"State {state.id}"
    else:
        return "Unknown State"


def format_messages(deserialized):
    updated = []

    for message in deserialized.messages:
        updated += ["{:<100s}".format(message.content)]

    return updated
