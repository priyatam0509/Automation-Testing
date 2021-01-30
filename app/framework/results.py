"""
Description: Module holds classes for reporting results of automated runs both
locally and remotely.

Original Author: Kyle Schneiderman
Date Created: 11/22/2016
Edited by: Conor McWain
Date Edited: 3/17/2020
"""
import requests, datetime, logging, os
import string, random

from jinja2 import Environment, FileSystemLoader

log = logging.getLogger()

class Results:
    global indiv_tag
    indiv_tag = False

    def initilize(self, brand, version, attempt_num, title = "Regression", location=".\\output\\standalone"):
        global configuration, run_token, env, data

        log.info(f"Logging results here: {location}")
        # First, any configurations are stored here
        configuration = {
            'template_loc': '.\\templates\\',
            'results_loc': location,
            'web_route': 'http://10.80.31.212/api/results/record'
        }

        # Some things we need to keep track of.
        run_token = ''.join([random.choice(string.ascii_letters+string.digits) for n in range(32)])
        log.debug(f"Current run token: {run_token}")
        env = Environment(loader=FileSystemLoader(configuration['template_loc']))
        data = {
            'fail': 0,
            'pass': 0,
            'brand': brand,
            'title': title,
            'runtime': datetime.datetime.strptime('00:00:00', '%H:%M:%S'),
            'date': datetime.datetime.now().strftime("%m.%d.%Y_%H%M%S"),
            'version': version,
            'attempt_num': attempt_num,
            'notes': {},
            'tests': []
        }

    def record(self, test_id, script_name, description, result, run_time, single_tc = False):
        """
        Records the result of a test case into a locally stored results file, as well as on web server

        Args:
            test_id: (string) The test case id
            script_name: (string) The name of the file where the test case lives
            description: (string) A short description of what the script does
            result: (string) Result of the script "passed"/"failed"
            run_time: (string) String representing test run time "00:00:00"

        Returns:
            None

        Examples:
            >>> import results
            >>> x = results.Results()
            >>> x.record("Some_test1", "random_tests.py", "Tests some thing", "00:01:32")
        """
        global configuration, run_token, env, data, indiv_tag

        log.info("Recording result")
        #Gather the information about the test execution
        runTime = run_time.split(":")
        data['tests'].append({
            'test_id': test_id,
            'script_name': script_name,
            'description': description,
            'run_time': run_time,
            'result': result.capitalize()
        })
        data['runtime'] = data['runtime'] + datetime.timedelta(hours=int(runTime[0]), minutes=int(runTime[1]), seconds=int(runTime[2]))
        #Determine if we want to increment the pass/fail counter by one
        if single_tc:
            #If logging TCs within methods this will prevent duplicate counting when we log the method
            indiv_tag = True
            data[result] += 1
        else:
            #Make sure we haven't already logged a test from this method
            if indiv_tag:
                log.debug("Already logged a test for this method. Not adding to the count.")
                indiv_tag = False
            else:
                data[result] += 1

        log.info(f"Adding test: {test_id}, {script_name}, {description}, {run_time}, {result.capitalize()}")

        # We need to go ahead and send a request to the web server
        try:
            r = requests.post(configuration['web_route'], data={
                'token': run_token,
                'brand': data['brand'],
                'case': test_id,
                'name': script_name,
                'title': data['title'],
                'description': description,
                'version': data['version'],
                'result': result.lower(),
                'run_time': (int(runTime[0])*3600 + int(runTime[1]) * 60 + int(runTime[2]))
            })
        except requests.exceptions.RequestException as e:
            log.error('Results were not uploaded to server')
            log.error(str(e))
            data['notes']['connection'] = 'Results were not uploaded to server'

        # Does the directory already exist?
        template = env.get_template('results.template.html')
        # output/<test_suite_name>/<build_name>/*_<attempt_num>.html
        filename = f"{configuration['results_loc']}/{data['title']}_results_{data['attempt_num']}.html"
        log.info(f"Attempting to save file: {filename}")

        #filename = configuration['results_loc'] + "\\" + data['version'] + "\\results\\" + data['version'] + '_' + data['date'] + "\\" + data['title'] + '.html'
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as e:
                log.error("There was an error creating the directory for results storage")
                log.error(str(e))

        # Great, let's output our results
        with open(filename, 'w+') as f:
            f.write(template.render(data))
            f.close()

#TEST CODE
if __name__ ==  "__main__":
    print("Hello there")
