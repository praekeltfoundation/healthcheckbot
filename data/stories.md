## happy path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## unhappy path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries
    
## very unhappy path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
* chitchat
    - utter_chitchat
    - healthcheck_form
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## stop but continue path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* affirm
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## stop and really stop path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}

## chitchat stop but continue path
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
* stop
    - utter_ask_continue
* affirm
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## stop but continue and chitchat path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* affirm
    - healthcheck_form
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## chitchat stop but continue and chitchat path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
* stop
    - utter_ask_continue
* affirm
    - healthcheck_form
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## chitchat, stop and really stop path
* greet
    - utter_greet
* request_healthcheck
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}


## bot challenge
* bot_challenge
  - utter_iamabot
