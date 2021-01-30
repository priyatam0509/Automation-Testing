import argparse
import importlib
import json
import logging
import os
import sys
import time
import types
import inspect
import pywinauto
from threading import Lock
from datetime import date, datetime
from textwrap import TextWrapper

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from app import initial_setup, Overlay, Results, system, crindsim
from app.framework import EDH
from app import server

SCRIPTS_DIR = "scripts/features"
TIME_FMT = "%Y-%m-%dT%H:%M:%S"
RUN_DATA_FILE = "C:/Automation/run_info.json"
PASS = True
FAIL = False
LOCK = Lock()
verbosity = logging.INFO
log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
default_log_level = "DEBUG"
site_type = "passport"
run_info = {}
start_time = None

#region Questions
'''
NOTE:
1. There are two questions asking for clarification on TODO comments in load_methods
'''
#endregion

#region Issues
'''
FIXME:
'''
#endregion

#region Enhancements
'''
TODO:
1. In load_methods we want to change a try except to type verification
2. In load_methods we want to add logging if we skip adding a test that has been specified
    a. (If the test is specifically called but doesn't have the @test decorator)
'''
#endregion

# suite funcs
def run_info_dump():
    """
    Run Info Dump

    The run_info dictionary is used to update (overwrite) the RUN_DATA_FILE.
    """
    global run_info

    with LOCK:
        with open(RUN_DATA_FILE, 'w') as sdf:
            json.dump(run_info, sdf, indent=4)

def load_methods(feature, attribute = "_test", names=[]):
    """
    Load Methods

    This method will parse the feature file provided and returns a list of methods that have a decorator
    matching the attribute variable provided. If a list of TCs is present in the suite file only those TCs
    will be checked.

    Args:
        feature (str):      The name of the script you are trying to load the methods from.
        attribute (str):    The decorator of the tests you want to load. Defaults to '_test'.
        names (list):       The names of the methods to load. All will be loaded by default.

    Returns:
        methods (list):     A list of methods that match the attribute provided.
    """
    log = logging.getLogger()

    #Load the class object of the feature
    class_ref = load_class_ref(feature)
    try:
        ref = class_ref()
    except:
        log.error("There was an issue with the class reference")
        system.print_full_stack()
        raise

    methods = []
    # Import methods
    for name in dir(ref):
        attr = getattr(ref, name)
        if getattr(attr, attribute, False) and (not names or attr.__name__ in names):        
            methods.append(attr)
    return methods

def load_class_ref(feature):
    """
    Load Class Reference

    This method will load the class reference for the feature file provided.

    Args:
        feature (str):      The name of the script you are trying to load the class reference from.

    Returns:
        class_ref (ref):     A class reference of the feature provided
    """
    log = logging.getLogger()

    #If there are specific tests to add we have to work through the dict
    if type(feature) == dict:
        #https://www.python.org/dev/peps/pep-0448/
        key = [*feature][0]
        feature_file = f'scripts/features/{key}'
        module_name = f'Scripts.features.{key.replace(".py", "")}'
    else:
        feature_file = f'scripts/features/{feature}'
        module_name = f'Scripts.features.{feature.replace(".py", "")}'

    #Make sure the file we want exists
    if not os.path.isfile(feature_file):
        log.error(f"Failed to find the specified python file: {feature_file}")
        return

    #Load the file/class
    class_name = os.path.basename(feature_file).replace('.py', '')
    test = importlib.import_module(module_name, "")
    class_ref = getattr(test, class_name)
    return class_ref

def setup_run(name, log_verbosity, variables):
    """
    Setup Run

    This method will create and populate the run_info file and starts the log instances

    Args:
        name (str):             The name of the script where the methods are located.
        log_verbosity (str):    The desired default verbosity for the current execution.
        variables (str):        A string comprised of key, value pairs that have been passed in at runtime.
    """
    global run_info

    # In case the user included .json or .py in the file name
    test_name = name.replace('.json', '')
    test_name = name.replace('.py', '')

    if not os.path.exists("C:/Automation"):
        os.makedirs("C:/Automation")

    try:
        with LOCK:
            with open(RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
        #Check if we should update or replace the run_info file
        if test_name == run_info['name']:
            update_runinfo(variables)
        else:
            create_runinfo(variables, test_name)
    except:
        create_runinfo(variables, test_name)

    # Checking to see if the log path exists. If not, then create it.
    if not os.path.exists(run_info['logs_dir']):
        os.makedirs(run_info['logs_dir'])

    # Starting the log.
    log = logging.getLogger()
    log.setLevel(log_verbosity)
    log.propagate = False
    
    exceptionLog = logging.getLogger("exceptionLog")
    exceptionLog.setLevel(logging.CRITICAL)
    exceptionLog.propagate = False

    #Configure the FileHandlers
    fh = logging.FileHandler(f"{run_info['logs_dir']}/{run_info['log_name']}")
    fh.setLevel(log_verbosity)

    exceptionfh = logging.FileHandler(f"{run_info['logs_dir']}/{run_info['log_name']}")
    exceptionfh.setLevel(logging.CRITICAL)
    
    #Configure and set the Formatters
    formatter = logging.Formatter('[%(asctime)s]: [%(name)s] [%(levelname)s] [%(funcName)s] %(message)s',
                                '%m/%d/%Y %I:%M:%S %p')
    fh.setFormatter(formatter)
    
    exceptionFormatter = logging.Formatter('%(message)s')
    exceptionfh.setFormatter(exceptionFormatter)

    console_logger = logging.StreamHandler(stream=sys.stdout)
    console_logger.setFormatter(formatter)

    error_console_logger = logging.StreamHandler()
    error_console_logger.setFormatter(exceptionFormatter)
    
    #Add the configured FileHandler to the logger
    log.addHandler(fh)
    log.addHandler(console_logger)
    exceptionLog.addHandler(exceptionfh)
    exceptionLog.addHandler(error_console_logger)
    

def create_runinfo(variables, test_name):
    """
    Create run_info

    This method will establish the values we want in a new run_info file and then create the file with those values

    Args:
        variables (str):    A string comprised of key, value pairs that have been passed in at runtime.
    """
    global run_info

    #Previous code may have failed due to an invalid file
    try:
        os.remove(RUN_DATA_FILE)
    except:
        pass
    
    run_info['name'] = test_name
    run_info['attempt_num'] = 1
    run_info['version'] = system.get_version()
    run_info['brand'] = system.get_brand().upper()
    run_info['date_started'] = date.today().strftime('%Y%m%d')
    run_info['date_started_full'] = datetime.now().strftime(TIME_FMT)
    run_info['output_dir'] = f"output/{test_name}_"+datetime.now().strftime("%m%d-%H%M")
    run_info['logs_dir'] = run_info['output_dir']+"/logs"
    run_info['results_dir'] = run_info['output_dir']+"/results"
    run_info['log_name'] = f"{test_name}_{run_info['attempt_num']}.log"
    run_info['current test name'] = ""

    if variables != None:
        var_pair = variables.split(',')
        for var in var_pair:
            _vars = var.split(':')
            run_info[_vars[0]] = _vars[1]

    run_info_dump()

def update_runinfo(variables):
    """
    Update run_info

    This method will add any variables passed in by the tester and update the attempt number and log name in run_info

    Args:
        variables (str):    A string comprised of key, value pairs that have been passed in at runtime.
    """
    global run_info

    if variables != None:
        var_pair = variables.split(',')
        for var in var_pair:
            _vars = var.split(':')
            run_info[_vars[0]] = _vars[1]

    run_info['attempt_num'] = run_info['attempt_num'] + 1
    run_info['log_name'] = f"{run_info['name']}_{run_info['attempt_num']}.log"

    run_info_dump()
    
def end_test(test_name, result, reason=""):
    """
    Start Test

    This method will create and populate the run_info file and starts the log instances

    Args:
        test_name (str):    The name of the test we are starting.
        result (str):       The result of the test execution.
        reason (str):       The reason for the failure of the test execution.
    """
    log = logging.getLogger()

    log.info("-" * 60)
    if result == PASS:
        log.info(f"| {test_name} Passed.")
    else:
        system.takescreenshot()
        # this should go into the new log.failure() thingy... that we don't have yet
        log.error(f"| {test_name} failed with reason: {reason}.")
    log.info("-" * 60)

def execute(test, tests_to_run=[]):
    """
    Execute

    This method will execute the test or suite provided

    Args:
        test (str):     The name of the test(s) being run.
        tests_to_run (list): The names of the test cases to run within the script. All will be run by default. 
                             N/A for suites; tests to run must be specified within the suite JSON.
    """
    global run_info

    log = logging.getLogger()
           
    res = Results()
    res.initilize(run_info['brand'], run_info['version'], run_info['attempt_num'], run_info['name'], run_info['results_dir'])
    feature_tests = {}
    suite = False

    log.info("-" * 60)
    log.info(f"| Starting {run_info['name']}: {run_info['date_started']}")
    log.info("-" * 60)

    if '.py' not in test and '.json' not in test:
        log.error("Failed to identify file as a script or suite file")
        return False

    if '.py' in test:
        script_file = f'scripts/features/{test}'
        #Verify the Script file exists
        if not os.path.isfile(script_file):
            log.warning(f"No such script: {script_file}")
            return False

        #The formats we return
        #feature_list = 'TestScript.py'
        feature_list = [test]

    elif '.json' in test:
        # Dismiss 'passport intalled' prompt
        pywinauto.mouse.click(button='left', coords=(420, 430))

        suite = True
        suite_file = f'scripts/{test}'
        #Verify the Suite JSON file exists
        if os.path.isfile(suite_file):
            #Parse the Suite JSON file
            with open(suite_file) as suite_list:
                try:
                    suite = json.load(suite_list)
                except:
                    # we know the file exists.. 
                    log.error(f"Invalid json file: {suite_file}")
                    return False
        else:
            log.warning(f"No such suite: {suite_file}")
            return False

        feature_list = suite['suite_features']

        #Try/Except for backwards compatibility
        try:
            #Check the `initial_Setup` value
            if suite['initial_setup']:
                IS = initial_setup.Initial_setup(site_type)
                IS.basic_setup()
        except KeyError:
            IS = initial_setup.Initial_setup(site_type)
            IS.basic_setup()

    for test in feature_list:
        test_name = test
        if type(test) == dict: # For parsing suite files that specify TCs within a script
            # The code that does this for CMD line is located in the main method. This could use cleaning up.
            test_name = [*test][0]
            tests_to_run = test[test_name]
        execute_test(test_name, res, tests_to_run)

    now = datetime.now().replace(microsecond=0)
    diff = now - start_time
    
    log.info('-'*60)
    log.info(f"| Finished run at {now}")
    log.info('-'*60)
    log.info(f"| Suite run time: {diff}")
    log.info('-'*60)

def execute_test(script, res, tests_to_run=[]):
    """
    Execute Test

    This method will execute the script provided

    Args:
        script (str):       The name of the test we are executing.
        res (inst):         An instance of the Results class from the results module
        tests_to_run (list): The names of the test cases to run within the script/scripts to run within the suite.
                             All will be run by default.
    """
    global run_info

    log = logging.getLogger()
    
    #This tests list is in alpha-numeric order
    #The `load_methods` function will handle the logic of specific tests being executed
    try:
        tests = load_methods(script, "_test", tests_to_run)
        setup = load_methods(script, "_setup")
        teardown = load_methods(script, "_teardown")
    except:
        system.print_full_stack()
        log.error(f"There was an issue loading the methods from {script}")
        return

    #Check for and run the setup if it exists
    if len(setup) == 0:
        log.warning("There is no setup to run")
    else:
        setup = setup[0]
        log.info("Running setup")
        try:
            setup()
        except Exception as e:
            log.critical(f"{type(e).__name__}: {str(e)}")
            system.print_full_stack()        
            log.error("Caught an exception in setup, termininating this script.")
            return

    #This final_list is in order from the top down of the Class    
    class_ref = load_class_ref(script)
    final_list = []
    mod_source = inspect.getsourcelines(class_ref)
    for line in mod_source[0]:
        for method in tests:
            if "def %s(" %(method.__name__) in line:
                final_list.append(method)

    for test in final_list:
        #Pull the description out of the docstring
        try:
            docstr = test.__doc__.splitlines()
        except:
            docstr = ["Your docstrings are empty"]
        if docstr[0] == '':
            if docstr[1] == '':
                description = 'Description not available'
            else:
                description = docstr[1].strip()
        else:
            description = docstr[0].strip()

        #Set the test start time
        test_start = time.time()
        #Starting the Test logging
        log.info("-" * 60)
        log.info(f"| Starting tc {test.__name__}: {description}")
        log.info("-" * 60)
        run_info['current test name'] = test.__name__
        
        run_info_dump()

        try:
            test()
        except Exception as e:
            #Calculate the run time of the test (Fail)
            delta = time.time()-test_start
            m, s = divmod(delta, 60)
            h, m = divmod(m, 60)
            run_time = f"{int(h):02}:{int(m):02}:{int(s):02}"
            #Record the result in the html file
            res.record(test.__name__, script, description, "fail", run_time)
            #Update fields in run_info
            end_test(test.__name__, FAIL, str(e))
            #Hanlde if the Script continues with the next TC
            tp = type(e)
            if tp.__name__ == 'ScriptError':
                system.print_full_stack()
                log.info("Caught ScriptError, termininating this script.")
                break
            elif tp.__name__ == 'TestError':
                log.info("Caught TestError, recording result and continuing.")
                continue
            else:
                # if we get here, we have a problem in our framework most likely. Dump as much info as we can..
                log.critical(f"Unhandled exception: {str(e)}")
                system.print_full_stack()
                break

        #Calculate the run time of the test (Pass)
        delta = time.time()-test_start
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        run_time = f"{int(h):02}:{int(m):02}:{int(s):02}"
        #Record the result in the html file
        res.record(test.__name__, script, description, "pass", run_time)
        #Update fields in run_info
        end_test(test.__name__, PASS)

    #Check for and run the teardown if it exists
    if len(teardown) == 0:
        log.warning("There is no teardown to run")
    else:
        teardown = teardown[0]
        log.info("Running teardown")
        try:
            teardown()
        except:
            system.print_full_stack()
            log.error("Caught an exception in teardown.")
            return

    log.setLevel(verbosity)

def args_parser():
    """
    Arguments Parser

    This method will instantiate and populate the argparser with the arguments we accept and their helptext

    Arguments:
        site_type (str):    Specify if the machine is Passport, Edge or Self Checkout
        variable (str):     Custom variables that will be saved in the run_info.json file
        verbose:            By calling this argument you enable the debug log lines
        setup (str):        Call this to call any of the setup functions
                            Functions include:
                            f - Feature Activation
                            h - EDH Configuration
                            r - Register Configuration
                            n - Network Configuration
                            e - Employee Setup
                            x - Import XML
                            i - Basic Setup
        restore (str):      Provide a name of a snapshot to restore the system with
        new (str):          Create a new test with the name you provide
        run (str):          Execute the script/suite file provided
        tests (str):        A comma-separated string specifying the test cases to run. All tests will be run if not specified.

    Returns:
        argparser (ref): A reference to the argsparser object

    Examples:
        python test_harness.py -new New_Test
        python test_harness.py -setup fr
        python test_harness.py -setup i
        python test_harness.py -run Smoke_Test_MWS.py
        python test_harness.py -run Smoke_test_MWS.py -tests sign_on,sign_off
        python test_harness.py -v -run Smoke_Test.json
        python test_harness.py -v -run Smoke_Test_Edge.json -t edge        
        python test_harness.py -restore Clean_Snapshot
    """
    wrap = TextWrapper(initial_indent="", subsequent_indent="", width=70)
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                    description="Automation framework entry point",
                    argument_default=False)

    helptext = "\n".join(wrap.wrap("Sets the passport type being set up, options include: passport, edge, express."))
    argparser.add_argument("-type", "--site_type", help=helptext)

    helptext = "\n".join(wrap.wrap("Allows for variables to be passed in to a suite with the formatting: 'Key1:Value1,Key2:Value2'."))
    argparser.add_argument("-var", "--variable", help=helptext)

    helptext = "\n".join(wrap.wrap("Deprecated. Verbose logging is now the default. Use -l to change logging level."))
    argparser.add_argument("-v", "--verbose", help=helptext, action="store_true")

    helptext = "\n".join(wrap.wrap(f"Set the logging level. From most to least logging: {log_levels}. Default is {default_log_level}."))
    argparser.add_argument("-l", "--log", help=helptext, default="DEBUG")

    helptext = ("Execute initial setup steps. Specify one or more of the following args: \n" 
        "i: Initial Setup - includes all setup steps. Use this to set up a freshly installed site.\n"
        "f: Feature Activation\n" 
        "h: EDH configuration - fake hardening, carwash controller sim, reg entries for CRIND Sim \n" 
        "r: Register Setup\n" 
        "n: Network Setup\n" 
        "e: Employee configuration\n" 
        "x: Extraction Tool Import - Pricebook, Forecourt, Speed Keys, Store Options, etc.\n")
    argparser.add_argument("-setup", "--setup", help=helptext, default=False)

    helptext = "\n".join(wrap.wrap("Restores the specified Snapshot."))
    argparser.add_argument("-restore", "--restore", help=helptext)

    helptext = '\n'.join(wrap.wrap("Creates a new test from a template " +
                                   "with name NEW_TEST that can immediately be " + 
                                   "used to automate."))
    argparser.add_argument("-new", "--new", help=helptext)

    helptext = '\n'.join(wrap.wrap(f"The name of the test or suite to run."))
    argparser.add_argument("-run", "--run", default='None', help=helptext)

    helptext = '\n'.join(wrap.wrap(f"Run specific test cases from a script. Provide test method names to run separated by commas. N/A for suites."))
    argparser.add_argument("-tests", "--tests", help=helptext)

    return argparser

if __name__ == '__main__':
    #Load the logging instance
    log = logging.getLogger()

    start_time = datetime.now().replace(microsecond=0)
    if not os.path.exists(SCRIPTS_DIR):
        os.mkdir(SCRIPTS_DIR)

    #Load the arguments parser and parse the arguments provided
    parser = args_parser()
    args = parser.parse_args()

    #If the verbosity argument is provided turn the logging level to `DEBUG`
    if not args.log:
        verbosity = logging.DEBUG
    else:
        if args.log.upper() not in log_levels:
            log.error(f"{args.log} is not a valid logging level. Valid levels include: {log_levels}.")
            system._toggle_win_state('restore', ['Command Prompt'])
            sys.exit(0)
        verbosity = getattr(logging, args.log.upper())


    #If site_type argument is provided and on the list set the `site_type` variable to the provided value
    if args.site_type:
        # Checking if the passed in site type matches one that is expected
        if args.site_type.lower() not in ['passport', 'edge', 'express']:
            log.error(f"The site type: {args.site_type} does not match a known site type")
            system._toggle_win_state('restore', ['Command Prompt'])
            sys.exit(0)

        # otherwise, go ahead and set it.
        site_type = args.site_type.lower()

    #If the variable argument is provided set the value provided to the `variables` variable.
    if args.variable:
        variables  = args.variable
    else:
        variables = None

    tests_to_run = []
    if args.tests:
        tests_to_run = args.tests.replace(' ', '').split(',')

    #Minimize all windows
    log.debug("Minimizing all windows that are not Passport related.")
    system._toggle_win_state('minimize')

    #If the restore argument is provided restore the snapshot with the name provided then stop
    if args.restore:
        system.restore_snapshot(args.restore)
        system._toggle_win_state('restore', ['Command Prompt'])
        sys.exit(0)

    #If the setup argument is provided excecute the relevant method(s) of initial setup
    if args.setup:
        setup_run("Running Setup", verbosity, variables)
        #Initialize the initial_setup module
        IS = initial_setup.Initial_setup(site_type)
        if 'f' in args.setup:
            log.info('Running Feature Activation')
            IS.feature_activate(site_type)
        if 'h' in args.setup:
            log.info('Running EDH Config')
            IS.setup_edh()
        if 'r' in args.setup:
            log.info('Configuring a Register')
            IS.configure_register()
        if 'n' in args.setup:
            #TODO: PDL support?
            log.info('Running Network Setup')
            IS.setup_network()
        if 'e' in args.setup:
            log.info('Running Employee Setup')
            IS.add_employee()
        if 'x' in args.setup:
            #TODO: Add custom xml support
            log.info('Running Import XML')
            IS.edit_xml()
            IS.import_xml()
        if 'i' in args.setup:
            log.info('Running Initial Setup')
            IS.basic_setup()

    #Evalutate if new_test argument is provided and creates the new test with the provided name
    elif args.new:
        setup_run("New Suite", verbosity, variables)
        log.info('Creating a new test')
        system.new_test(args.new)
    #Evalutate if run argument is provided and executes the variable provided
    elif args.run != 'None':
        setup_run(args.run, verbosity, variables)
        log.info(f'Running {args.run}')
        execute(f"{args.run}", tests_to_run)
    else:
        parser.print_help()

    #Restore the Command Prompt so the user knows the automation has completed
    system._toggle_win_state('restore', ['Command Prompt'])