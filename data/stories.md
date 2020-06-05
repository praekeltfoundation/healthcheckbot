## happy path
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - slot{"requested_slot": "province"}
* form: inform{"number": "2"}
    - slot{"province": "fs"}
    - form: restaurant_form
    - slot{"requested_slot": "age"}
* form: inform{"number": "1"}
    - slot{"age": "<18"}
    - form: restaurant_form
    - slot{"requested_slot": "cough"}
* form: inform{"number": "2"}
    - slot{"cough": "no"}
    - form: restaurant_form
    - slot{"requested_slot": "exposure"}
* form: inform{"number": "3"}
    - slot{"exposure": "not sure"}
    - form: restaurant_form
    - slot{"requested_slot": "tracing"}
* form: inform{"number": "1"}
    - slot{"tracing": "yes"}
    - form{"name": null}
    - utter_slots_values

## bot challenge
* bot_challenge
  - utter_iamabot
