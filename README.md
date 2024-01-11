# Taipei Day Trip 🧳

SPA RWD Web App using Python/Flask & MySQL.

- port on 3000

# Demo Account



| Demo Inout     |  value                                 |
|-----------------------|---------------------------------------------------|
| ID    |  demo@gmail.com                        |
| PW   | 123456Aa@                           |

## Test Card Number

Only supports Direct Pay test env

Token Pay must use REAL credit card. It won't cost any balance in test env

The due date  : You can just use any date after today.

| Card Number           | CCV  | Response                                          |
|-----------------------|------|---------------------------------------------------|
| 4242 4242 4242 4242   | 123  | 0 - Success (type: Visa)                          |
| 3543 9234 8838 2426   | 123  | 0 - Success (type: JCB)                           |
| 3454 5465 4604 563    | 1234 | 0 - Success (type: AMEX)                          |
| 5451 4178 2523 0575   | 123  | 0 - Success (type: MASTERCARD)                    |
| 6234 5774 3859 4899   | 123  | 0 - Success (type: UnionPay)                      |
| 4716 3139 6829 4359   | 123  | 0 - Success (type: Visa)                          |
| 4242 4202 3507 4242   | 123  | 915 - Unknown Error, please contact TapPay       |
| 4242 4216 0218 4242   | 123  | 10003 - Card Error                                |
| 4242 4222 0418 4242   | 123  | 10005 - Bank System Error                         |
| 4242 4240 1026 4242   | 123  | 10006 - Duplicate Transaction                     |
| 4242 4246 1228 4242   | 123  | 10008 - Bank Merchant Account Data Error          |
| 4242 4264 1829 4242   | 123  | 10009 - Amount Error                              |
| 4242 4276 2229 4242   | 123  | 10013 - Order number duplicate                    |
| 4242 4288 2639 4242   | 123  | 10023 - Bank Error                                |
| 4242 4210 0008 4242   | 123  | 10015 - Redeem Failed                             |

## Technique


| Name         | Des  | Familiarity                                         |
|-----------------------|------|---------------------------------------------------|
| Figma  | Frontend Design | Familiar                    |
| Html/Css(SCSS)/JavaScript   | Frontend | Familiar                    |
| Python3 / Flask  | Backend| some familiar                         |
| MySQL | Database | some familiar                         |
| Amazon Web Service (AWS) EC2 Instance   | server(ubuntu, Linux) | some familiar                    |
| Elastic IP | AWS | some familiar   |
| Nginx | Server on Linux | some familiar   |
| MySQL | Database on Linux | some familiar     |
| CloudFlare  | DNS | some familiar     |
| HTTPS SSH | SSH | some familar |
| Gunicorn | Flask Server on Linux | some familar |

Using 4 processes on Gunicorn. 
Using port 3000 (alike Flask 3000) instead of Unix sock to simplify the process.

User => Domain => CloudFlare DNS => AWS EC2 ubuntu server => Nginx => Gunicorn (Port 3000) 




