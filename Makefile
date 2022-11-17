default: dist

dist: clean intbase.py run_autograder setup.sh tester.py harness.py failsv1 testsv1 failsv2 testsv2 failsv3 testsv3
	zip -r grader.zip intbase.py run_autograder setup.sh tester.py harness.py failsv1 testsv1 failsv2 testsv2 failsv3 testsv3

clean:
	rm -f grader.zip
	rm -f results.json
