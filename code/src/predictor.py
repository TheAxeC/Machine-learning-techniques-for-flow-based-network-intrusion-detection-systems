
class Failure:

    def __init__(self, result, correct, index):
        self.result = result
        self.correct = correct
        self.index = index

    def string(self):
        return "Expected " + str(self.correct) + " Got: " + str(self.result) + " Indexed " + str(self.index) + "\n"

# The failure records class
class Failures:

    def __init__(self):
        self.fails = 0
        self.records = []

    def add_fail_record(self, result, correct, i):
        self.records.append(Failure(result, correct, i))
        self.fails = self.fails + 1

    def results(self, totals, minimize=False):
        ret = "Ratio of: " + str(float(totals - self.fails) / float(totals) * 100.0) + "% with " + str(self.fails) + " fails and"
        ret += " a total of " + str(totals) + " precictions"

        if minimize:
            return ret

        ret += "\n"
        for f in self.records:
            ret += f.string()
        ret += "\n"

        return ret

class Result:

    def __init__(self, flow, result):
        self.flow = flow
        self.result = result



# A predictor class
class Predictor:

    def __init__(self, print_total=False):
        self.totals = 0
        self.fails = Failures()
        self.returns = []

        self.start = 0
        self.finish = 0
        self.check = False

        self.algorithm = None
        self.minimize = not print_total

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def runner(self, data_set, check):
        for d in data_set:
            "Start file: " + str(d) + "."
            self.predict_file(d, check=True)
            "End file: " + str(d) + "."
        print self.results()

    def predict_file(self, d, check=False):
        from loader import NetflowLoader
        loader = NetflowLoader()
        loader.load(d['file'], d['from'], d['to'])

        samples = loader.get_netflow()
        self.predict(samples, check=True)

    def predict(self, flow, check=False):
        if self.algorithm:
            self.check = check
            self.loop(flow)
        else:
            print "Please set an algorithm first."

    def loop(self, netflow):
        i = 0
        while i < netflow.get_size():
            result = self.algorithm.predict(netflow.get_sample_data()[i])
            if self.check:
                test = result == netflow.get_target_data()[i]
                if not test:
                    self.fails.add_fail_record(result, netflow.get_target_data()[i], i)
            else:
                self.returns.append(Result(netflow.get_sample_data()[i], result))
            i = i + 1
            self.totals = self.totals + 1

    def results(self):
        if self.check:
            return self.fails.results(self.totals, minimize=self.minimize)
        return self.returns

    def reset(self):
        self.totals = 0
        self.fails = Failures()
        self.returns = []

        self.start = 0
        self.finish = 0
        self.check = False