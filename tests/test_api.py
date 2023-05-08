import unittest
import requests
from opp import rest_api
import multiprocessing
import time
import json

class APIStart():

    #Launch the API in background and wait a bit
    @classmethod
    def setUpClass(cls):
        cls.api_process = multiprocessing.Process(target=rest_api.run)
        cls.api_process.start()
        time.sleep(1)

    #Stop the execution
    @classmethod
    def tearDownClass(cls):
        cls.api_process.terminate()


class TestInitialFilters(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = "toto"

    """
    OK
    {'value': 'Paris','type': 'location','positive': True},{'value': 'Paul Martin','type': 'name','positive': True}
    """
    def test_init_filters_1(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "{'value': 'Paris','type': 'location','positive': True},{'value': 'Paul Martin','type': 'name','positive': True}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)

    """
    OK
    [{'value': 'Paris','type': 'location','positive': True}]
    """
    def test_init_filters_2(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)
    """
    KO
    missing starting {
    {'value': 'Paris','type': 'location','positive': True
    """
    def test_init_filters_3(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "{'value': 'Paris','type': 'location','positive': True")
        self.assertEqual(response.status_code, 400, "missing starting {")

    """
    KO
    missing {} and []
    'value': 'Paris','type': 'location','positive': True
    """
    def test_init_filters_4(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "'value': 'Paris','type': 'location','positive': True")
        self.assertEqual(response.status_code, 400)

    """
    KO
    not a list, neither a list element
    {'type': 'location','positive': True
    """
    def test_init_filters_5(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "{'type': 'location','positive': True")
        self.assertEqual(response.status_code, 400)

    """
    KO
    missing value
    [{'type': 'location','positive': True}]
    """
    def test_init_filters_6(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 400)
    
    """
    KO
    missing type
    [{'value': 'Paris','positive': True}]
    """
    def test_init_filters_7(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','positive': True}]")
        self.assertEqual(response.status_code, 400)

    """
    OK
    [{'value': 'Paris','type': 'location','positive': True},{'value': 'Paul Martin','type': 'name','positive': True}]
    """
    def test_init_filters_8(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','type': 'location','positive': True},{'value': 'Paul Martin','type': 'name','positive': True}]")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)

    """
    KO
    missing positive value
    [{'value': 'Paris','type': 'location'}]
    """
    def test_init_filters_9(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','type': 'location'}]")
        self.assertEqual(response.status_code, 400)
    
    """
    KO
    still missing positive value, method not mandatory
    [{'value': 'Paris','type': 'location', 'method': 'google'}]
    """
    def test_init_filters_10(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','type': 'location', 'method': 'google'}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    missing } at the end
    ['value': 'Paris','type': 'location','positive': True}]
    """
    def test_init_filters_11(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "['value': 'Paris','type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 400)

    """
    OK 
    [{'positive': True, 'value': 'Paris', 'type': 'location'}]
    """
    def test_init_filters_12(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'positive': True, 'value': 'Paris', 'type': 'location'}]")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)

    """
    KO
    wrong type
    [{'value': 'Paris','type': 'toto','positive': True}]
    """
    def test_init_filters_13(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'Paris','type': 'toto','positive': True}]")
        self.assertEqual(response.status_code, 400)
    
    """
    KO
    too long value
    [{'value': 'a*1000','type': 'location','positive': True}]
    """
    def test_init_filters_14(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value':" +  'a'*1000 + "',type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 400)
    
    """
    KO
    positive value must be a boolean
    [{'value': 'London','type': 'location','positive': 'test'}]
    """
    def test_init_filters_15(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'London','type': 'location','positive': 'test'}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    too long method value
    [{'value': 'London','type': 'location','positive': False, 'method': 'a'*100 }]
    """
    def test_init_filters_16(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'London','type': 'location','positive': False, 'method':" + 'a'*100 +  "}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    *100 in the method value
    [{'value': 'London','type': 'location','positive': False, 'method': 'a'*100 }]
    """
    def test_init_filters_17(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'London','type': 'location','positive': False, 'method': 'a'*100 }]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    True must start with a capital letter
    [{'value': 'London','type': 'location','positive': true}]
    """
    def test_init_filters_18(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'London','type': 'location','positive': true}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    True must start with a capital letter
    [{'value': 'London','type': 'location','positive': True}]
    """
    def test_init_filters_19(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'London','type': 'location','positive': true}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    Must handle code injection
    [{'value': 'DELETE * FROM clients','type': 'location','positive': True}]
    """
    def test_init_filters_20(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'DELETE * FROM clients','type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 400)
    
    """
    KO
    code injection
    [{'value': 'DELETE','type': '* FROM clients','positive': True}]
    """
    def test_init_filters_21(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': 'DELETE','type': '* FROM clients','positive': True}]")
        self.assertEqual(response.status_code, 400)

    """
    KO
    note valid json input, missing ''
    [{'value': test','type': 'location','positive': True}]
    """
    def test_init_filters_22(self):
        response = requests.get(self.url + 'target=' + self.target + '&initial_filters=' + "[{'value': test','type': 'location','positive': True}]")
        self.assertEqual(response.status_code, 400)

class TestTarget(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = ""

    """
    OK
    valid target input
    target: 'test input'
    """
    def test_target_1(self):
        self.target = 'test_input'
        response = requests.get(self.url + 'target=' + self.target)
        self.assertEqual(response.status_code, 200)
        



def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True
    

if __name__ == '__main__':
    APIStart.setUpClass()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestInitialFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestTarget))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    APIStart.tearDownClass()

        