#### This file contains tests to evaluate that your bot behaves as expected.
#### If you want to learn more, please see the docs: https://legacy-docs-v1.rasa.com/user-guide/testing-your-assistant/

## happy path healthcheck
* request_healthcheck: check
  - slot{"terms": null}
  - utter_welcome
  - healthcheck_terms_form
  - form{"name": "healthcheck_terms_form"}
  - form{"name": null}
  - action_start_triage
  - healthcheck_profile_form
  - form{"name": "healthcheck_profile_form"}
  - form{"name": null}
  - action_assign_study_b_arm
  - honesty_check_form
  - form{"name": "honesty_check_form"}
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
  - action_start_triage
  - healthcheck_profile_form
  - form{"name": "healthcheck_profile_form"}
  - form{"name": null}
  - action_assign_study_b_arm
  - honesty_check_form
  - form{"name": "honesty_check_form"}
  - form{"name": null}
  - utter_start_health_check
  - healthcheck_form
  - form{"name": "healthcheck_form"}
  - form{"name": null}
  - action_send_study_messages
  - action_session_start
