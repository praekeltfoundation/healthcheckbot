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
    - action_session_start

## session start new
    - action_session_start
    - slot{"terms": null}

## session start returning
    - action_session_start
    - slot{"terms": "yes"}

## request exit
* exit
    - utter_exit
    - action_session_start

## interactive exit in terms form
* request_healthcheck
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"requested_slot": "terms"}
* exit
    - action_deactivate_form
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_exit

## interactive exit in profile form
* request_healthcheck
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"requested_slot": "terms"}
* form: affirm
    - form: healthcheck_terms_form
    - slot{"terms": "yes"}
    - form{"name": null}
    - slot{"requested_slot": null}
    - healthcheck_profile_form
    - form{"name": "healthcheck_profile_form"}
    - slot{"requested_slot": "age"}
* exit
    - action_deactivate_form
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_exit

## interactive exit in healthcheck form
* request_healthcheck
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"requested_slot": "terms"}
* form: affirm
    - form: healthcheck_terms_form
    - slot{"terms": "yes"}
    - form{"name": null}
    - slot{"requested_slot": null}
    - healthcheck_profile_form
    - form{"name": "healthcheck_profile_form"}
    - slot{"requested_slot": "age"}
* form: inform{"number": "2"}
    - form: healthcheck_profile_form
    - slot{"age": "18-39"}
    - slot{"requested_slot": "gender"}
* form: inform{"number": "3"}
    - form: healthcheck_profile_form
    - slot{"gender": "OTHER"}
    - slot{"requested_slot": "province"}
* form: inform{"number": "9"}
    - form: healthcheck_profile_form
    - slot{"province": "wc"}
    - slot{"requested_slot": "location"}
* form: inform{"province": "cape"}
    - form: healthcheck_profile_form
    - slot{"location": "cape town"}
    - slot{"requested_slot": "location_confirm"}
* form: inform{"number": "1"}
    - form: healthcheck_profile_form
    - slot{"location_confirm": "yes"}
    - slot{"requested_slot": "medical_condition"}
* form: inform{"number": "2"}
    - form: healthcheck_profile_form
    - slot{"medical_condition": "no"}
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_start_health_check
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - slot{"requested_slot": "symptoms_fever"}
* exit
    - action_deactivate_form
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_exit

## interactive_story_1
* request_healthcheck
    - utter_welcome
    - healthcheck_terms_form
    - form{"name": "healthcheck_terms_form"}
    - slot{"requested_slot": "terms"}
* form: exit
    - form: healthcheck_terms_form
    - slot{"terms": null}
    - slot{"requested_slot": "terms"}
    - action_deactivate_form
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_exit
