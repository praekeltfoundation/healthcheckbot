## happy path
* request_healthcheck
    - slot{"terms": null}
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"terms": null}
    - slot{"terms": "yes"}
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

## happy path returning user
* request_healthcheck
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

## session start new
    - action_session_start
    - slot{"terms": null}

## session start returning
    - action_session_start
    - slot{"terms": "yes"}

## child keyword new
* child
    - action_set_profile_obo
    - slot{"terms": null}
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"terms": null}
    - slot{"terms": "yes"}
    - form{"name": null}
    - healthcheck_profile_form
    - form{"name": "healthcheck_profile_form"}
    - form{"name": null}
    - utter_start_health_check
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - action_session_start

## child keyword returning
* child
    - action_set_profile_obo
    - slot{"terms": "yes"}
    - utter_welcome_back
    - healthcheck_profile_form
    - form{"name": "healthcheck_profile_form"}
    - form{"name": null}
    - utter_start_health_check
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - action_session_start

## exit
* exit
    - action_exit
    - slot{"terms": null}
    - action_listen
