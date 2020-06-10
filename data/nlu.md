## intent:request_healthcheck
- Hi! I want to do health check for myself
- I want to do a test for myself
- Test
- Healthcheck
- Health check
- Please check if I have covid
- Please check if I'm sick
- Please check if I have to get tested
- I want to get tested
- Please test
- Test me 
- Do I have the virus?
- Do I need to get tested?
- Check my symptoms
- I have a fever! Do I have covid?
- check

## intent:affirm
- correct
- ye
- uh yes
- let's do it
- yeah
- uh yes
- um yes
- that's correct
- yes yes
- right
- yea
- yes
- yes right
- i do

## intent:deny
- no
- no thanks
- no thank you
- uh no
- breath no

## intent:maybe
- not sure
- maybe
- i'm not sure
- i don't know

## lookup:province
data/lookup_tables/provinces.txt

## intent:inform
- I live in [gauteng]{"entity": "province", "value": "gt"}
- I live in the [western cape]{"entity": "province", "value": "wc"}
- [eastern cape]{"entity": "province", "value": "ec"}
- [free state]{"entity": "province", "value": "fs"}
- [gauteng]{"entity": "province", "value": "gt"}
- [gp]{"entity": "province", "value": "gt"}
- [kzn]{"entity": "province", "value": "nl"}
- [kwazulu-natal]{"entity": "province", "value": "nl"}
- [kwazulu natal]{"entity": "province", "value": "nl"}
- [natal]{"entity": "province", "value": "nl"}
- [limpopo]{"entity": "province", "value": "lp"}
- [mpumalanga]{"entity": "province", "value": "mp"}
- [north west]{"entity": "province", "value": "nw"}
- [northwest]{"entity": "province", "value": "nw"}
- [northern cape]{"entity": "province", "value": "nc"}
- [western cape]{"entity": "province", "value": "wc"}
- [1](number)
- [2](number).

## regex:number
- \d+
