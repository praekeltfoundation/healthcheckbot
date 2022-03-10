#### This file contains tests to evaluate that your bot behaves as expected.
#### If you want to learn more, please see the docs: https://legacy-docs-v1.rasa.com/user-guide/testing-your-assistant/

## happy path healthcheck
* request_healthcheck: check
  - slot{"terms": null}
  - utter_welcome
  - healthcheck_terms_form
  - form{"name": "healthcheck_terms_form"}
  - form{"name": null}
  - healthcheck_profile_form
  - form{"name": "healthcheck_profile_form"}
  - form{"name": null}
  - utter_start_health_check
  - healthcheck_form
  - form{"name": "healthcheck_form"}
  - form{"name": null}
  - action_send_study_messages
  - action_session_start

## happy path healthcheck returning user
* request_healthcheck: check
  - slot{"terms": "yes"}
  - utter_welcome_back
  - healthcheck_profile_form
  - form{"name": "healthcheck_profile_form"}
  - form{"name": null}
  - utter_start_health_check
  - healthcheck_form
  - form{"name": "healthcheck_form"}
  - form{"name": null}
  - action_send_study_messages
  - action_session_start
