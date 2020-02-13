from state_pb2 import *
import unittest


def generate_test_states():

    """ 
    Generates 102 (simulated) ready, busy, killed states
    ready states have ID equivalent to 0 mod 3
    busy states have ID equivalent to 1 mod 3
    killed states have ID equivalent to 2 mod 3

    Busy and killed states are also given custom 'reasons' (i.e. messages) to describe 
    why the states have stopped executing instructions or why they have been killed.

    Busy states are given non-default IDs (.id) , wait times (.wait_time), and number of
    executing instructions (.num_executing).

    StateList objects may be described as arrays of State objects, which may then be serialized
    and deserialized via protobuf.

    """

    busy_states = StateList()
    ready_states = StateList()
    killed_states = StateList()

    for ready_id, busy_id, killed_id in map(
        lambda x: (x, x + 1, x + 2), range(0, 100, 3)
    ):
        rstate = State()
        bstate = State()
        kstate = State()

        rstate.type = State.READY
        rstate.id = ready_id

        bstate.type = State.BUSY
        bstate.id = busy_id
        bstate.num_executing = 10
        bstate.wait_time = 2
        bstate.reason = "Timeout"

        kstate.type = State.KILLED
        kstate.id = killed_id
        kstate.reason = "Killed by user"

        ready_states.states.extend([rstate])
        busy_states.states.extend([bstate])
        killed_states.states.extend([kstate])

    return ready_states, busy_states, killed_states


class TestStateGeneration(unittest.TestCase):
    def test_state_creation_defaults(self):

        """ 
        Initiates a blank state and checks to see if default values 
        are correct
        """

        s = State()
        self.assertEqual(s.id, 0)
        self.assertEqual(s.type, State.READY)
        self.assertEqual(s.num_executing, 0)
        self.assertEqual(s.reason, "")
        self.assertEqual(s.wait_time, 0)

    def test_state_creation(self):

        """ 
        Initiates a (non-default) busy state and checks to see if values 
        are passed in and updated successfully
        """
        s = State()
        s.id = 100
        s.type = State.BUSY
        s.num_executing = 5
        s.reason = "Execution terminated"
        s.wait_time = 10

        self.assertEqual(s.id, 100)
        self.assertEqual(s.type, State.BUSY)
        self.assertEqual(s.num_executing, 5)
        self.assertEqual(s.reason, "Execution terminated")
        self.assertEqual(s.wait_time, 10)

    def test_serialization(self):
        """ 
        Tests to see if serialization / deserialization works properly for State objects
        """
        s = State()
        s.id = 100
        s.type = State.BUSY
        s.num_executing = 5
        s.reason = "Execution terminated"
        s.wait_time = 10

        serialized = s.SerializeToString()
        s2 = State()
        s2.ParseFromString(serialized)

        self.assertEqual(s, s2)

    def test_StateList(self):
        """ 
        Initiates 3 StateLists using the function above and checks to see if State values 
        are passed in and updated successfully
        """
        ready, busy, killed = generate_test_states()

        for ready_state in ready.states:
            self.assertEqual(ready_state.id % 3, 0)
            self.assertEqual(ready_state.type, State.READY)
            self.assertEqual(ready_state.num_executing, 0)
            self.assertEqual(ready_state.reason, "")
            self.assertEqual(ready_state.wait_time, 0)

        for busy_state in busy.states:
            self.assertEqual(busy_state.id % 3, 1)
            self.assertEqual(busy_state.reason, "Timeout")
            self.assertEqual(busy_state.type, State.BUSY)
            self.assertEqual(busy_state.num_executing, 10)
            self.assertEqual(busy_state.wait_time, 2)

        for killed_state in killed.states:
            self.assertEqual(killed_state.id % 3, 2)
            self.assertEqual(killed_state.type, State.KILLED)
            self.assertEqual(killed_state.num_executing, 0)
            self.assertEqual(killed_state.reason, "Killed by user")
            self.assertEqual(killed_state.wait_time, 0)

    def test_StateList_serialization(self):
        """ 
        Tests to see if serialization/deserialization works properly for StateList objects
        """
        ready, busy, killed = generate_test_states()

        ready_serialized = ready.SerializeToString()
        busy_serialized = busy.SerializeToString()
        killed_serialized = killed.SerializeToString()

        ready_deserialized = StateList()
        busy_deserialized = StateList()
        killed_deserialized = StateList()

        ready_deserialized.ParseFromString(ready_serialized)
        busy_deserialized.ParseFromString(busy_serialized)
        killed_deserialized.ParseFromString(killed_serialized)

        self.assertEqual(ready_deserialized, ready)
        self.assertEqual(busy_deserialized, busy)
        self.assertEqual(killed_deserialized, killed)

    def test_LogMessage_creation(self):
        """ 
        Tests to see if instantiation works properly for LogMessage objects
        """
        message = LogMessage()
        message.content = "AAAAAAAA"
        self.assertEqual(message.content, "AAAAAAAA")

    def test_MessageList_creation(self):
        """ 
        Tests to see if instantiation works properly for MessageList objects
        """
        message = LogMessage()
        message.content = "AAAAAAAA"
        message2 = LogMessage()
        message2.content = "BBBBBBBB"

        message_list = MessageList()
        message_list.messages.extend([message])
        message_list.messages.extend([message2])

        self.assertEqual(message_list.messages[0], message)
        self.assertEqual(message_list.messages[1], message2)

    def test_LogMessage_serialization(self):
        """ 
        Tests to see if serialization/deserialization works properly for LogMessage objects
        """
        message = LogMessage()
        message.content = "AAAAAAAA"
        message2 = LogMessage()
        message2.ParseFromString(message.SerializeToString())
        self.assertEqual(message, message2)

    def test_MessageList_serialization(self):
        """ 
        Tests to see if serialization/deserialization works properly for MessageList objects
        """
        message = LogMessage()
        message.content = "AAAAAAAA"
        message2 = LogMessage()
        message2.content = "BBBBBBBB"

        message_list = MessageList()
        message_list.messages.extend([message])
        message_list.messages.extend([message2])

        message_list_deserialized = MessageList()
        message_list_deserialized.ParseFromString(message_list.SerializeToString())
        self.assertEqual(message_list_deserialized, message_list)


if __name__ == "__main__":
    unittest.main()
