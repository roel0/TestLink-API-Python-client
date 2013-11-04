#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2013 Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ------------------------------------------------------------------------

# this test works WITHOUT an online TestLink Server
# no calls are send to a TestLink Server

import unittest
#from testlink import TestlinkAPIGeneric, TestLinkHelper
from testlink import testlinkerrors
from testlink import testlinkapigeneric
#from testlink.testlinkapigeneric import positionalArgNamesDefault
# scenario_a includes response from a testlink 1.9.8 server
SCENARIO_A = {'repeat' : 'You said: One World',
              'sayHello' : 'Hey Folks!',
              'doesUserExist' : {
                'Big Bird' :  [{'message': '(doesUserExist) - Cannot Find User Login provided (Big Bird).', 
                                'code': 10000}],
                'admin' : True },
              'getProjectTestPlans' : {
                'onePlan' : [{'name': 'TestPlan_API', 
                         'notes': 'New TestPlan created with the API', 
                         'active': '1', 'is_public': '1', 
                         'testproject_id': '21', 'id': '22'}] ,
                'noPlan' : '' },
              'getBuildsForTestPlan' : {'noBuild' : '' },
              'getTestPlanPlatforms' : {
                'twoPlatforms' : [{'notes': '', 'id': '1', 'name': 'dutch'}, 
                                  {'notes': '', 'id': '2', 'name': 'platt'}],
                'noPlatform' : [{'message': 'Test plan (noPlatform) has no platforms linked', 
                         'code': 3041}]},
              'getTestSuitesForTestPlan' : {'noSuite' : ''},
              'getTestSuitesForTestSuite' : {'noSuite' : ''},
              'getFirstLevelTestSuitesForTestProject' : {
                'noSuite' : [{'message': 'Test Project (noSuite) is empty.', 
                              'code': 7008}]},
              'getTestCasesForTestSuite' : {'noTestCase' : [] },
              'getTestCasesForTestPlan'  : {'noTestCase' : [] },
              'getTestCaseIDByName' : {
                'dictResult' :  {'1': {'parent_id': '24', 'tc_external_id': '2', 
                                       'id': '33', 'tsuite_name': 'B - First Level', 
                                       'name': 'TESTCASE_B'}}, 
                'listResult' : [{'parent_id': '25', 'tc_external_id': '1', 
                                 'id': '26', 'tsuite_name': 'AA - Second Level', 
                                 'name': 'TESTCASE_AA'}]}
              }

class DummyAPIGeneric(testlinkapigeneric.TestlinkAPIGeneric):
    """ Dummy for Simulation TestLinkAPIGeneric. 
    Overrides 
    - _callServer() Method to return test scenarios
    - extend positional_arg_names for  method 'DummyMethod'
    """

    __slots__ = ['scenario_data', 'callArgs']
  
    def __init__(self, server_url, devKey):
        super(DummyAPIGeneric, self).__init__(server_url, devKey)
        self._positionalArgNames['DummyMethod'] = ['Uno', 'due', 'tre']
        self.scenario_data = {}
        self.callArgs = None


    def loadScenario(self, a_scenario):
        self.scenario_data = a_scenario

    def _callServer(self, methodAPI, argsAPI=None):
        self.callArgs = argsAPI
        response = None
        if methodAPI in ['DummyMethod']:
            response = [argsAPI]
        else:
            data = self.scenario_data[methodAPI]
            if methodAPI in ['doesUserExist']:
                response = data[argsAPI['user']]
            elif methodAPI in ['getProjectTestPlans', 
                               'getFirstLevelTestSuitesForTestProject']:
                response = data[argsAPI['testprojectid']]
            elif methodAPI in ['getBuildsForTestPlan', 'getTestPlanPlatforms', 
                        'getTestSuitesForTestPlan', 'getTestCasesForTestPlan']:
                response = data[argsAPI['testplanid']]
            elif methodAPI in ['getTestSuitesForTestSuite', 
                               'getTestCasesForTestSuite']:
                response = data[argsAPI['testsuiteid']]
            elif methodAPI in ['getTestCaseIDByName']:
                response = data[argsAPI['testcasename']]
            else:
                response = data
        return response
    
    
class TestLinkAPIGenericOfflineTestCase(unittest.TestCase):
    """ TestCases for TestlinkAPIGeneric - does not interacts with a TestLink Server.
    works with DummyAPIGeneric which returns special test data
    """

    def setUp(self):
        self.api = testlinkapigeneric.TestLinkHelper().connect(DummyAPIGeneric)
        self.callArgs = None
        
#    def tearDown(self):
#        pass


    def test_convertPositionalArgs(self):
        response = self.api._convertPostionalArgs('DummyMethod',  [1,2,3])
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3}, response)
        
    def test__convertPositionalArgs_missingConf(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('NoConfigMethod',  [1,2])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)
        
    def test__convertPositionalArgs_lessValues(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('DummyMethod',  [1,2])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)
        
    def test__convertPositionalArgs_moreValues(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('DummyMethod',  [1,2,3,4])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)

    def test_callServerWithPosArgs_pos(self):
        self.api.callServerWithPosArgs('DummyMethod',  1,2,3)
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3}, self.api.callArgs)

    def test_callServerWithPosArgs_pos_opt(self):
        self.api.callServerWithPosArgs('DummyMethod',  1,2,3, quad=4)
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3, 'quad' : 4}, self.api.callArgs)

    def test_callServerWithPosArgs_opt(self):
        self.api.callServerWithPosArgs('DummyMethod',  quad=4)
        self.assertEqual({'quad' : 4}, self.api.callArgs)

    def test_callServerWithPosArgs_none(self):
        self.api.callServerWithPosArgs('DummyMethod')
        self.assertEqual({}, self.api.callArgs)
        
    def test_checkResponse_emptyResponse(self):
        client = self.api
        def a_func(a_api, response): 
            a_api._checkResponse(response, 'DummyMethod',  
                                 {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, '')
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, [])
        
    def test_checkResponse_errorResponse(self):
        client = self.api
        responseA = [{'message': '(reportTCResult) - TC ID 709 does not exist!', 
                      'code': 5000}]
        def a_func(a_api, response): 
            a_api._checkResponse(response, 'DummyMethod',  
                                 {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, 
                          responseA)

    def test_checkResponse_okResponse(self):
        self.api._checkResponse(
                        [{'message': 'all fine, cause no key with name code'}],
                         'DummyMethod', {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.api._checkResponse(
                        'some API Call juts returns one string without codes',
                         'DummyMethod', {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_checkResponse_booleanResponse(self):
        response = True
        self.api._checkResponse(response, 'DummyMethod', 
                                {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_checkResponse_dictionaryResponse(self):
        response = {'note' : 'uploadAttachment Calls return {..} and not [{..}]'}
        self.api._checkResponse(response, 'DummyMethod', 
                                {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_ping(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.ping()
        self.assertEqual('Hey Folks!', response)
        
    def test_noWrapperName_decoApiCallWithoutArgs(self):
        " decorator test: original function name should be unchanged "
        @testlinkapigeneric.decoApiCallWithoutArgs
        def orig_funcname1(a_api):
            "orig doc string"
            return 'noArgs'
        
        self.assertEqual('orig_funcname1', orig_funcname1.__name__)
        self.assertEqual('orig doc string', orig_funcname1.__doc__)
        self.assertEqual('testlinkapigeneric_offline_test', orig_funcname1.__module__)

    def test_decoApiCallWithArgs(self):
        " decorator test: positional and optional arguments should be registered "
        @testlinkapigeneric.decoMakerApiCallWithArgs(['Uno', 'due', 'tre'], ['quad'])
        def DummyMethod(a_api):
            "a dummy api method with 3 positional args and 1 optional arg"
            pass
        posArgs = testlinkapigeneric.getMethodsWithPositionalArgs()
        print posArgs
        self.assertEqual(['Uno', 'due', 'tre'], posArgs['DummyMethod'])

    def test_noWrapperName_decoApiCallWithArgs(self):
        " decorator test: original function name should be unchanged "
        @testlinkapigeneric.decoMakerApiCallWithArgs()
        def orig_funcname2(a_api):
            "orig doc string"
            return 'noArgs'
        
        self.assertEqual('orig_funcname2', orig_funcname2.__name__)
        self.assertEqual('orig doc string', orig_funcname2.__doc__)
        self.assertEqual('testlinkapigeneric_offline_test', orig_funcname2.__module__)

    def test_decoApiCallAddDevKey(self):
        " decorator test: argsOptional should be extended with devKey"
        testlinkapigeneric.registerMethod('a_func')
        @testlinkapigeneric.decoApiCallAddDevKey
        def a_func(a_api, *argsPositional, **argsOptional):
            return argsPositional, argsOptional
        # check method argument definition
        allArgs = testlinkapigeneric.getApiArgsForMethod('a_func')
        self.assertEqual(['devKey'], allArgs)
        # check call arguments
        response = a_func(self.api)
        self.assertEqual({'devKey' : self.api.devKey}, response[1])

    def test_noWrapperName_decoApiCallAddDevKey(self):
        " decorator test: original function name should be unchanged "
        testlinkapigeneric.registerMethod('orig_funcname3')
        @testlinkapigeneric.decoApiCallAddDevKey
        def orig_funcname3(a_api, *argsPositional, **argsOptional):
            "orig doc string"
            return argsPositional, argsOptional
        
        self.assertEqual('orig_funcname3', orig_funcname3.__name__)
        self.assertEqual('orig doc string', orig_funcname3.__doc__)
        self.assertEqual('testlinkapigeneric_offline_test', orig_funcname3.__module__)
        
    def test_decoApiCallReplaceTLResponseError_NoCodeError(self):
        " decorator test: TLResponseError (code=None) should be handled "
        @testlinkapigeneric.decoMakerApiCallReplaceTLResponseError()
        def a_func(a_api, *argsPositional, **argsOptional):
            raise testlinkerrors.TLResponseError('DummyMethod', 
                                argsOptional, 'Empty Response! ')

        response = a_func(self.api)
        self.assertEqual([], response)
        
    def test_decoApiCallReplaceTLResponseError_CodeError(self):
        " decorator test: TLResponseError (code=777) should be raised "
        @testlinkapigeneric.decoMakerApiCallReplaceTLResponseError()
        def a_func(a_api, *argsPositional, **argsOptional):
            raise testlinkerrors.TLResponseError('DummyMethod', 
                                argsOptional, 'Empty Response! ', 777)

        with self.assertRaisesRegexp(testlinkerrors.TLResponseError, 
                                     '777.*Empty'):
            a_func(self.api)
        
    def test_decoApiCallReplaceTLResponseError_CodeErrorOk(self):
        " decorator test: TLResponseError (code=777) should be handled "
        @testlinkapigeneric.decoMakerApiCallReplaceTLResponseError(777)
        def a_func(a_api, *argsPositional, **argsOptional):
            raise testlinkerrors.TLResponseError('DummyMethod', 
                                argsOptional, 'Empty Response! ', 777)

        response = a_func(self.api)
        self.assertEqual([], response)

    def test_decoApiCallReplaceTLResponseError_NoError(self):
        " decorator test: response without TLResponseError should be passed "
        @testlinkapigeneric.decoMakerApiCallReplaceTLResponseError()            
        def a_func(a_api, *argsPositional, **argsOptional):
            return argsOptional

        response = a_func(self.api, name='BigBird')
        self.assertEqual({'name' : 'BigBird'}, response)

    def test_noWrapperName_decoApiCallReplaceTLResponseError(self):
        " decorator test: original function name should be unchanged "
        @testlinkapigeneric.decoMakerApiCallReplaceTLResponseError()
        def orig_funcname4(a_api, *argsPositional, **argsOptional):
            "orig doc string"
            return argsPositional, argsOptional
        
        self.assertEqual('orig_funcname4', orig_funcname4.__name__)
        self.assertEqual('orig doc string', orig_funcname4.__doc__)
        self.assertEqual('testlinkapigeneric_offline_test', orig_funcname4.__module__)
        
    def test_noWrapperName_apiMethods(self):
        " decorator test: API Methods internal function name should be unchanged "
        
        # apiMethod with decorator @decoApiCallWithoutArgs
        self.assertEqual('sayHello', self.api.sayHello.__name__)
        # apiMethod with decorator @decoApiCallWithArgs
        self.assertEqual('repeat', self.api.repeat.__name__)
        # apiMethod with decorator @decoApiCallAddDevKey 
        self.assertEqual('createBuild', self.api.createBuild.__name__)
        # apiMethod with decorator @decoMakerApiCallReplaceTLResponseError()
        self.assertEqual('getProjectTestPlans', self.api.getProjectTestPlans.__name__)
        

        
    def test_getProjectTestPlans_noPlan(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getProjectTestPlans('noPlan')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getProjectTestPlans_onePlan(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getProjectTestPlans('onePlan')
        self.assertEqual('21', response[0]['testproject_id'])
        self.assertEqual(1, len(response))
        
    def test_getBuildsForTestPlan_noBuild(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getBuildsForTestPlan('noBuild')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getTestPlanPlatforms_noPlatform(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestPlanPlatforms('noPlatform')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getTestPlanPlatforms_twoPlatforms(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestPlanPlatforms('twoPlatforms')
        self.assertEqual('dutch', response[0]['name'])
        self.assertEqual(2, len(response))

    def test_getTestSuitesForTestPlan_noSuite(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestSuitesForTestPlan('noSuite')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
       
    def test_getTestSuitesForTestSuite_noSuite(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestSuitesForTestSuite('noSuite')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getFirstLevelTestSuitesForTestProject_noSuite(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getFirstLevelTestSuitesForTestProject('noSuite')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getTestCasesForTestSuite_noTestCase(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestCasesForTestSuite('noTestCase')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
           
    def test_getTestCasesForTestPlan_noTestCase(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestCasesForTestPlan('noTestCase')
        self.assertEqual([], response)
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getTestCaseIDByName_dictResult(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestCaseIDByName('dictResult', 
                                            testprojectname='NEW_PROJECT_API')
        self.assertEqual(dict, type(response))
        self.assertEqual('TESTCASE_B', response['1']['name']) 
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
    def test_getTestCaseIDByName_listResult(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.getTestCaseIDByName('listResult')
        self.assertEqual(list, type(response))
        self.assertEqual('TESTCASE_AA', response[0]['name']) 
        self.assertEqual(self.api.devKey, self.api.callArgs['devKey'])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()