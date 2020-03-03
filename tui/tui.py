import npyscreen
import drawille
import logging
import socket
import select
import warnings
import threading
import time

from state_pb2 import StateList, State, MessageList
from format_states import format_state, format_messages
from google.protobuf.message import DecodeError

warnings.filterwarnings("ignore")

HOST = "localhost"
PORT = 3214
npyscreen.BufferPager.DEFAULT_MAXLEN = 10000  # Maximum number of log messages to buffer


state_model = {"ready": [], "busy": [], "killed": [], "terminated": []}
log_buffer = []
state_lock = threading.Lock()
log_lock = threading.Lock()
finished = False

logging.basicConfig(
    filename="mcore_tui_logs",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


class ManticoreTUI(npyscreen.NPSApp):
    def __init__(self):
        # List of all received states and messages

        self.keypress_timeout_default = 1

        self._logger = logging.getLogger("TUI")
        self._connected = False

    def draw(self):
        # Draws the main TUI form with all sub-widgets and allows for user interaction
        self.MainForm = ManticoreMain(parentApp=self)
        self.prev_width, self.prev_height = drawille.getTerminalSize()
        self.MainForm.edit()

    def while_waiting(self):
        # Saves current terminal size to determine whether or not a redraw
        # of the TUI is necessary
        curr_width, curr_height = drawille.getTerminalSize()

        if curr_width != self.prev_width or curr_height != self.prev_height:
            self._logger.info("Size changed")
            self.MainForm.erase()
            self.draw()
            self.MainForm.DISPLAY()

        locked = state_lock.acquire(blocking=False)
        if locked:
            try:
                self.MainForm.ready_state_widget.entry_widget.values = [
                    format_state(st) for st in state_model["ready"]
                ]
                self.MainForm.busy_state_widget.entry_widget.values = [
                    format_state(st) for st in state_model["busy"]
                ]
                self.MainForm.terminated_state_widget.entry_widget.values = [
                    format_state(st) for st in state_model["terminated"]
                ]
                self.MainForm.killed_state_widget.entry_widget.values = [
                    format_state(st) for st in state_model["killed"]
                ]
            finally:
                state_lock.release()

        locked = log_lock.acquire(blocking=False)
        if locked:
            try:
                self.MainForm.messages_widget.entry_widget.buffer(log_buffer)
                log_buffer.clear()
            finally:
                log_lock.release()

        # Updates the list of states and messages to be displayed
        # Normally appending to the list of values during while_waiting() would work but we have to
        # Consider the scenario where the user resizes the terminal, in which case
        # .erase() is called and all widgets lose their previous values upon being redrawn.
        # So we maintain a separate list of all currently received states and messages (all_states, all_messages)
        # and reassign Each widget's list of states / messages instead.

        self.MainForm.ready_state_widget.name = (
            f"Ready States ({len(self.MainForm.ready_state_widget.values)})"
        )
        self.MainForm.busy_state_widget.name = (
            f"Busy States ({len(self.MainForm.busy_state_widget.values)})"
        )
        self.MainForm.terminated_state_widget.name = (
            f"Terminated States ({len(self.MainForm.terminated_state_widget.values)})"
        )
        self.MainForm.killed_state_widget.name = (
            f"Killed States ({len(self.MainForm.killed_state_widget.values)})"
        )
        self.MainForm.messages_widget.name = (
            f"Log Messages ({len(self.MainForm.messages_widget.values)})"
        )

        self.MainForm.ready_state_widget.display()
        self.MainForm.busy_state_widget.display()
        self.MainForm.terminated_state_widget.display()
        self.MainForm.killed_state_widget.display()
        self.MainForm.messages_widget.display()

    def main(self):
        self.draw()

    def exit_cleanly(self, *_args):
        print("Exiting!")
        global finished
        finished = True
        exit()


def fetch_update():
    logger = logging.getLogger("FetchThread")
    while not finished:
        try:
            # Attempts to (re)connect to manticore server
            log_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug("Connecting to %s:%s", HOST, PORT)
            log_sock.connect((HOST, PORT))
            logger.info("Connected to %s:%s", HOST, PORT)

            read_sockets, write_sockets, error_sockets = select.select(
                [log_sock], [], [], 60
            )

            serialized = b""
            if read_sockets:
                serialized = read_sockets[0].recv(10000)
                logger.info("Pulled {} bytes".format(len(serialized)))

                try:
                    m = MessageList()
                    m.ParseFromString(serialized)
                    with log_lock:
                        formatted = format_messages(m)
                        log_buffer.extend(formatted)
                        logger.info("Deserialized LogMessage")

                except DecodeError:
                    logger.info("Unable to deserialize message, malformed response")

            read_sockets[0].shutdown(socket.SHUT_RDWR)

        except socket.error:
            logger.warning("Log Socket disconnected")
            log_sock.close()

        try:
            # Attempts to (re)connect to manticore server
            state_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug("Connecting to %s:%s", HOST, PORT + 1)
            state_sock.connect((HOST, PORT + 1))
            logger.info("Connected to %s:%s", HOST, PORT + 1)

            read_sockets, write_sockets, error_sockets = select.select(
                [state_sock], [], [], 60
            )

            serialized = b""
            if read_sockets:
                serialized = read_sockets[0].recv(10000)
                logger.info("Pulled {} bytes".format(len(serialized)))

                try:
                    m = StateList()
                    m.ParseFromString(serialized)

                    logger.info("Got %d states", len(m.states))

                    if len(m.states) > 0:
                        with state_lock:
                            new_model = {
                                "ready": [],
                                "busy": [],
                                "killed": [],
                                "terminated": [],
                            }
                            mapping = {
                                State.READY: "ready",
                                State.BUSY: "busy",
                                State.KILLED: "killed",
                                State.TERMINATED: "terminated",
                            }
                            for st in m.states:
                                for k in mapping:
                                    if st.type == k:
                                        new_model[mapping[k]].append(st)
                            global state_model
                            state_model = new_model

                        logger.info("Rendered %d states", len(m.states))

                except DecodeError:
                    logger.info("Unable to deserialize message, malformed response")

            state_sock.shutdown(socket.SHUT_RDWR)

        except socket.error:
            logger.warning("State Socket disconnected")
            state_sock.close()

        time.sleep(0.5)


class AutoScrollBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.BufferPager


class ManticoreMain(npyscreen.FormBaseNew):
    def create(self):

        height, width = self.useable_space()
        box_height = int(height * 0.35)
        box_width = int(width * 0.245)

        self.ready_state_widget = self.add(
            npyscreen.BoxTitle,
            name="Ready States",
            max_height=box_height,
            max_width=box_width,
            rely=1,
            editable=True,
        )

        self.busy_state_widget = self.add(
            npyscreen.BoxTitle,
            name="Busy States",
            max_height=box_height,
            max_width=box_width,
            relx=box_width + 2,
            rely=1,
            editable=True,
        )

        self.terminated_state_widget = self.add(
            npyscreen.BoxTitle,
            name="Terminated States",
            max_height=box_height,
            max_width=box_width,
            relx=width - 2 * box_width - 2,
            rely=1,
            editable=True,
        )

        self.killed_state_widget = self.add(
            npyscreen.BoxTitle,
            name="Killed States",
            max_height=box_height,
            max_width=box_width,
            relx=width - box_width - 2,
            rely=1,
            editable=True,
        )

        self.messages_widget = self.add(
            AutoScrollBox,
            name="Log Messages",
            # max_height=int(height * 0.62),
            editable=True,
        )

        self.add_handlers({"q": self.parentApp.exit_cleanly})


def main():
    global finished
    try:
        tui = ManticoreTUI()
        fetch_thread = threading.Thread(target=fetch_update)
        fetch_thread.start()
        tui.run()
    except KeyboardInterrupt:
        tui.exit_cleanly()


if __name__ == "__main__":
    main()
