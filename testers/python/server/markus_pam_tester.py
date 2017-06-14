import contextlib

from markus_tester import MarkusTester, MarkusTest
from pam_tester import PAMTester
from uam_tester import UAMResult
from markus_utils import MarkusUtils


class MarkusPAMTester(MarkusTester):
    """
    A wrapper to run the Python AutoMarker (pam - https://github.com/ProjectAT/uam) within Markus' test framework.
    """

    def __init__(self, path_to_uam, specs, test_timeout=5, global_timeout=20, feedback_file='feedback_python.txt'):
        super().__init__(specs=specs, feedback_file=feedback_file)
        self.pam_tester = PAMTester(path_to_uam=path_to_uam, specs=specs, test_timeout=test_timeout,
                                    global_timeout=global_timeout, result_filename='result.json')

    def run(self):
        try:
            with contextlib.ExitStack() as stack:
                feedback_open = (stack.enter_context(open(self.feedback_file, 'w'))
                                 if self.feedback_file is not None
                                 else None)
                results = self.pam_tester.run()
                for result in results:
                    points_awarded, points_total = self.pam_tester.get_test_points(result)
                    test = MarkusPAMTest(result, points_awarded, points_total, feedback_open)
                    xml = test.run()
                    print(xml)
        except Exception as e:
            MarkusUtils.print_test_error(name='All PYTHON tests', message=str(e))


class MarkusPAMTest(MarkusTest):

    def __init__(self, uam_result, points_awarded, points_total, feedback_open):
        test_name = (uam_result.name
                     if not uam_result.description
                     else '{} ({})'.format(uam_result.name, uam_result.description))
        super().__init__(test_name, [], {'points': points_total}, None, feedback_open)
        self.test_data_name = test_name
        self.uam_result = uam_result
        self.points_awarded = points_awarded

    def run(self):
        if self.uam_result.status == UAMResult.Status.PASS:
            return self.passed()
        elif self.uam_result.status == UAMResult.Status.FAIL:
            # TODO add test_solution=self.pam_result.trace? (But test trace could be confusing)
            return self.failed(points_awarded=self.points_awarded, message=self.uam_result.message)
        else:
            return self.error(message=self.uam_result.message)
