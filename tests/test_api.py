import unittest
import requests
from opp import rest_api
import multiprocessing
import time
import json
import random, string

class APIHandler():

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
        self.target = "test"

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
    test_input
    """
    def test_target_1(self):
        self.target = 'test_input'
        response = requests.get(self.url + 'target=' + self.target)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)

    """
    KO
    target input too long
    a*1002
    """
    def test_target_2(self):
        self.target = 'a'*1002
        response = requests.get(self.url + 'target=' + self.target)
        self.assertEqual(response.status_code, 400)

    """
    KO
    target input must be string
    'test'
    """
    def test_target_3(self):
        response = requests.get(self.url + 'target= "test"')
        self.assertEqual(response.status_code, 400)

    """
    KO
    target input should avoid injection code
    ;rm -rf /
    """
    def test_target_4(self):
        response = requests.get(self.url + 'target= ;rm -rf /')
        self.assertEqual(response.status_code, 400)
    
    """
    OK
    test input
    """
    def test_target_5(self):
        response = requests.get(self.url + 'target= test input')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        self.assertIs(validateJSON(response.text), True)

    """
    KO
    target field should not be empty
    """
    def test_target_6(self):
        response = requests.get(self.url + 'target=')
        self.assertEqual(response.status_code, 400)

class TestAPIKey(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = "test"

    """
    OK
    valid api_key input
    random api_key correct length
    """
    def test_api_key_1(self):
        response = requests.get(self.url + 'target=' + self.target + '&api_key=' + ''.join(random.choice(string.ascii_lowercase) for i in range(39)))
        self.assertEqual(response.status_code, 500)

    """
    KO
    invalid
    random api_key too long
    """
    def test_api_key_2(self):
        response = requests.get(self.url + 'target=' + self.target + '&api_key=' + ''.join(random.choice(string.ascii_lowercase) for i in range(40)))
        self.assertEqual(response.status_code, 400)


    """
    KO
    invalid api_key too short
    random api_key 38 of length
    """
    def test_api_key_3(self):
        response = requests.get(self.url + 'target=' + self.target + '&api_key=' + ''.join(random.choice(string.ascii_lowercase) for i in range(38)))
        self.assertEqual(response.status_code, 400)

    """
    KO
    code injection in the api_key
    
    """
    def test_api_key_4(self):
        response = requests.get(self.url + 'target=' + self.target + '&api_key=' + "<?php print('Please specify the name of the file to delete');print('<p>');$file=$_GET['filename'];system('rm $file');?>")
        self.assertEqual(response.status_code, 400)

class TestCSEId(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = "test"

    """
    OK
    valid cse_id input
    random cse_id correct length
    """
    def test_cse_id_1(self):
        response = requests.get(self.url + 'target=' + self.target + '&cse_id=' + ''.join(random.choice(string.ascii_lowercase) for i in range(17)))
        self.assertEqual(response.status_code, 500)

    """
    KO
    invalid
    random cse_id too long
    """
    def test_cse_id_2(self):
        response = requests.get(self.url + 'target=' + self.target + '&cse_id=' + ''.join(random.choice(string.ascii_lowercase) for i in range(18)))
        self.assertEqual(response.status_code, 400)

    """
    KO
    invalid cse_id too short
    random cse_id 38 of length
    """
    def test_cse_id_3(self):
        response = requests.get(self.url + 'target=' + self.target + '&cse_id=' + ''.join(random.choice(string.ascii_lowercase) for i in range(16)))
        self.assertEqual(response.status_code, 400)

    """
    KO
    code injection in the cse_id
    
    """
    def test_cse_id_4(self):
        response = requests.get(self.url + 'target=' + self.target + '&cse_id=' + "<?php print('Please specify the name of the file to delete');print('<p>');$file=$_GET['filename'];system('rm $file');?>")
        self.assertEqual(response.status_code, 400)

class TestDepth(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = "test"

    """
    OK
    correct integer between 1 and 10
    10
    """
    def test_depth_1(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=10')
        self.assertEqual(response.status_code, 200)

    """
    OK
    correct integer between 1 and 10
    1
    """
    def test_depth_2(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=1')
        self.assertEqual(response.status_code, 200)

    """
    KO
    string input
    "test"
    """
    def test_depth_3(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth="test"')
        self.assertEqual(response.status_code, 400)

    """
    KO
    empty input

    """
    def test_depth_4(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=')
        self.assertEqual(response.status_code, 400)

    """
    KO
    value > 10
    20
    """
    def test_depth_5(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=20')
        self.assertEqual(response.status_code, 400)

    """
    KO
    negative value
    -1
    """
    def test_depth_6(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=-1')
        self.assertEqual(response.status_code, 400)

    """
    KO?
    operation in the value field
    0.5*4
    """
    def test_depth_7(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=0.5*4')
        self.assertEqual(response.status_code, 400)

    """
    KO
    substraction in the value field
    5-3
    """
    def test_depth_8(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=5-3')
        self.assertEqual(response.status_code, 400)

    """
    KO
    division in the value field
    10/2
    """
    def test_depth_9(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=10/2')
        self.assertEqual(response.status_code, 400)

    """
    KO
    modulo in the value field
    10%2
    """
    def test_depth_10(self):
        response = requests.get(self.url + 'target=' + self.target + '&depth=10%2')
        self.assertEqual(response.status_code, 400)

class TestActiveSearch(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName=methodName)
        self.url = 'http://127.0.0.1:5000/api/?'
        self.target = "test"

    """
    OK
    correct input value
    0
    """
    def test_active_search_1(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=0')
        self.assertEqual(response.status_code, 200)

    """
    OK
    correct input value
    1
    """
    def test_active_search_2(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=1')
        self.assertEqual(response.status_code, 200)

    """
    KO
    incorrect input value too high
    2
    """
    def test_active_search_3(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=2')
        self.assertEqual(response.status_code, 400)

    """
    KO
    incorrect input: negative value
    -1
    """
    def test_active_search_4(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=-1')
        self.assertEqual(response.status_code, 400)

    """
    KO
    incorrect input: must be int not str
    test
    """
    def test_active_search_5(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=test')
        self.assertEqual(response.status_code, 400)

        """
    KO?
    operation in the value field
    0.5*2
    """
    def test_active_search_6(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=0.5*2')
        self.assertEqual(response.status_code, 400)

    """
    KO
    substraction in the value field
    5-3
    """
    def test_active_search_7(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=2-1')
        self.assertEqual(response.status_code, 400)

    """
    KO
    division in the value field
    2/4
    """
    def test_active_search_8(self):
        response = requests.get(self.url + 'target=' + self.target + '&active_search=2/4')
        self.assertEqual(response.status_code, 400)

 

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True
    

if __name__ == '__main__':
    APIHandler.setUpClass()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestInitialFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestTarget))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIKey))
    suite.addTests(loader.loadTestsFromTestCase(TestCSEId))
    suite.addTests(loader.loadTestsFromTestCase(TestDepth))
    suite.addTests(loader.loadTestsFromTestCase(TestActiveSearch))

    runner = unittest.TextTestRunner(verbosity=6)
    runner.run(suite)

    APIHandler.tearDownClass()

        