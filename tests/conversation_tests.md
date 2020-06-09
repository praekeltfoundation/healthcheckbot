#### This file contains tests to evaluate that your bot behaves as expected.
#### If you want to learn more, please see the docs: https://rasa.com/docs/rasa/user-guide/testing-your-assistant/

## happy path healthcheck
* request_healthcheck: check
  - action_reset_all_but_few_slots
  - healthcheck_form
  - form{"name": "healthcheck_form"}
  - form{"name": null}
  - utter_slots_values
