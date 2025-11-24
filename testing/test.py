from testing import sandbox
from testing.TsNeopixel1LineFake import TsNeopixel1LineFake

class Test:
    def __init__(self):
        self.testLine1Instance = TsNeopixel1LineFake()

    def run_test(self):
        server_packet = sandbox.query_server()
        self.testLine1Instance.update(server_packet)
        self.testLine1Instance.print_names()
        self.testLine1Instance.print_colors()


if __name__ == "__main__":
    testInstance = Test()
    testInstance.run_test()