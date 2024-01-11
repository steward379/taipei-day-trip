# Taipei Day Trip 🧳

- port on 3000

# Demo Account

ID : demo@gmail.com
PW : 123456Aa@

## Test Card Number

Only supports Direct Pay test env

Token Pay must use REAL credit card. It won't cost any balance in test env

The due date  : You can just use any date after today.

Card Number          	CCV     	Response
4242 4242 4242 4242	123	0 - Success ( type : Visa )
3543 9234 8838 2426	123	0 - Success ( type : JCB )
3454 5465 4604 563	1234	0 - Success ( type : AMEX )
5451 4178 2523 0575	123	0 - Success ( type : MASTERCARD )
使用此卡號進行 3D 驗證時會直接授權成功
6234 5774 3859 4899	123	0 - Success ( type : UnionPay )
4716 3139 6829 4359	123	0 - Success ( type : Visa )
使用此測試卡，會得到 bank_id 與 issuer_zh_tw 皆為空的情境
4242 4202 3507 4242	123	915 - Unknown Error, please contact TapPay customer service
4242 4216 0218 4242	123	10003 - Card Error
4242 4222 0418 4242	123	10005 - Bank System Error
4242 4240 1026 4242	123	10006 - Duplicate Transaction
4242 4246 1228 4242	123	10008 - Bank Merchant Account Data Error
4242 4264 1829 4242	123	10009 - Amount Error
4242 4276 2229 4242	123	10013 - Order number duplicate
4242 4288 2639 4242	123	10023 - Bank Error
4242 4210 0008 4242	123	10015 = Redeem Failed
