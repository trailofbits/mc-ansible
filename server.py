from state_pb2 import State, StateList, MessageList, LogMessage
import random
import time
import threading
import socketserver

HOST, PORT = "localhost", 3214

state_model = {"ready": [], "busy": [], "killed": [], "terminated": []}
state_lock = threading.Lock()

for max_state_id in range(1, random.randint(5, 10)):
    state_model["ready"].append(State(id=max_state_id))


def simulate_states():
    global max_state_id
    sl = "busy"
    for st in state_model[sl]:
        st.num_executing += random.randint(10, 100)
    i = 0
    while i < len(state_model[sl]):
        if random.random() > 0.2:
            i += 1
        else:
            st = state_model[sl].pop(i)
            action = random.choice(["kill"] + ["terminate"] * 4 + ["fork"] * 5)
            if action == "kill":
                st.type = State.KILLED
                st.reason = "Killed by user"
                state_model["killed"].append(st)
            if action == "terminate":
                st.type = State.TERMINATED
                st.reason = f"Execution returned {random.randint(0, 3)}"
                state_model["terminated"].append(st)
            if action == "fork":
                max_state_id += 1
                st1 = State(id=max_state_id, num_executing=st.num_executing)
                max_state_id += 1
                st2 = State(id=max_state_id, num_executing=st.num_executing)
                state_model["ready"].append(st1)
                state_model["ready"].append(st2)

    sl = "ready"
    while len(state_model["busy"]) < 4 and state_model[sl]:  # ncores=4
        if state_model[sl]:
            st = state_model[sl].pop(0)
            st.type = State.BUSY
            st.num_executing = 0
            state_model["busy"].append(st)


def render_states():

    state_array = StateList()

    for sl in state_model:
        for st in state_model[sl]:
            state_array.states.append(st)

    return state_array


def generate_messages():

    message_array = MessageList()

    message = LogMessage()
    message.content = f"This is a sample log message from {time.strftime('%b %d %Y %H:%M:%S', time.gmtime(time.time()))}"
    message_array.messages.append(message)

    return message_array


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        serialized_messages = generate_messages().SerializeToString()

        if random.random() >= 0.5:
            print("Sending messages")
            self.request.sendall(serialized_messages)
        else:
            with state_lock:
                print(
                    "Sending states::",
                    "Ready:",
                    len(state_model["ready"]),
                    "Busy:",
                    len(state_model["busy"]),
                    "Terminated:",
                    len(state_model["terminated"]),
                    "Killed:",
                    len(state_model["killed"]),
                )
                serialized_states = render_states().SerializeToString()
                self.request.sendall(serialized_states)

        time.sleep(1)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():

    # Create the server, binding to localhost on port 9999
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        try:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server_thread = threading.Thread(target=server.serve_forever)
            # Exit the server thread when the main thread terminates
            server_thread.daemon = True
            server_thread.start()
            print("Server loop running in thread:", server_thread.name)

            while True:
                time.sleep(random.randint(0, 3))
                with state_lock:
                    simulate_states()

        except KeyboardInterrupt:
            print("Shutting down gracefully")
            server.shutdown()


if __name__ == "__main__":
    main()
