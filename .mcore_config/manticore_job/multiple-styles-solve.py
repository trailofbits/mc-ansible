from manticore.native import Manticore

m = Manticore('multiple-styles')
m.context['flag'] = ""

@m.hook(0x400a3b)
def hook(state):
    cpu = state.cpu
    m.context['flag'] += chr(cpu.AL - 10)

@m.hook(0x400a3e)
def hook2(state):
    cpu = state.cpu
    cpu.ZF = True

@m.hook(0x400a40)
def hookf(state):
    print("Failed")
    m.terminate()

@m.hook(0x400a6c)
def hooks(state):
    print("Success!")
    print(m.context['flag'])
    m.terminate()

m.concrete_data = "12345678" * 2 + "\n"
m.run()
