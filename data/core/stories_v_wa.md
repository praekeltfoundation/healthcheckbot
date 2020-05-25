## Voluntary HealthCheck WhatsApp

## happy path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path 1st time no greet, accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path 1st time no greet, more + accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path nth time no greet, accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## happy path nth time no greet, more + accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries
    
## unhappy path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## unhappy path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## unhappy path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## unhappy path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* chitchat
    - utter_chitchat
    - healthcheck_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## very unhappy path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## very unhappy path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## very unhappy path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## very unhappy path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## stop but continue path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## stop but continue path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## stop but continue path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## stop but continue path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## stop and really stop path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}

## stop and really stop path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}

## stop and really stop path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}

## stop and really stop path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - healthcheck_form
    - form{"name": "healthcheck_form"}
* stop
    - utter_ask_continue
* deny
    - action_deactivate_form
    - form{"name": null}

## chitchat stop but continue path 1st time, accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat stop but continue path 1st time, more + accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat stop but continue path nth time, accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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
    
## chitchat stop but continue path nth time, more + accept T&C
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## stop but continue and chitchat path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## stop but continue and chitchat path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## stop but continue and chitchat path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## stop but continue and chitchat path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## chitchat stop but continue and chitchat path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat stop but continue and chitchat path 1st time, more accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat stop but continue and chitchat path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## chitchat stop but continue and chitchat path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## chitchat, stop and really stop path 1st time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat, stop and really stop path 1st time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "new"}
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_new
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
    - userdata_form
    - form{"name": "userdata_form"}
    - form{"name": null}
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

## chitchat, stop and really stop path nth time, accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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

## chitchat, stop and really stop path nth time, more + accept T&C
* greet
    - utter_greet
* request_healthcheck
    - action_get_user
    - slot{"user_status" : "returning"}
    - action_reset_all_but_few_slots
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "MORE"}
    - action_reset_terms
    - utter_more_info
    - utter_accept_tc_returning
    - terms_form
    - form{"name": "terms_form"}
    - slot{"terms_cond" : "ACCEPT"}
    - form{"name": null}
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
