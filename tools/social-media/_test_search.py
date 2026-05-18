import os, hmac, hashlib, base64, time, random, string, urllib.parse, urllib.request, urllib.error, ssl, json

def pct(s): return urllib.parse.quote(str(s), safe='')

ck  = os.environ['X_CONSUMER_KEY']
cs  = os.environ['X_CONSUMER_SECRET']
at  = os.environ['X_ACCESS_TOKEN']
ats = os.environ['X_ACCESS_TOKEN_SECRET']

timestamp = str(int(time.time()))
nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
base_url = 'https://api.twitter.com/2/tweets/search/recent'
query_params = {
    'query': '#AI活用 #中小企業 -is:retweet',
    'tweet.fields': 'public_metrics,author_id,created_at',
    'max_results': '10'
}

oauth = {
    'oauth_consumer_key': ck,
    'oauth_nonce': nonce,
    'oauth_signature_method': 'HMAC-SHA1',
    'oauth_timestamp': timestamp,
    'oauth_token': at,
    'oauth_version': '1.0'
}
all_p = {**oauth, **query_params}
param_str = '&'.join(pct(k) + '=' + pct(v) for k, v in sorted(all_p.items()))
base_str = '&'.join(['GET', pct(base_url), pct(param_str)])
sig = base64.b64encode(
    hmac.new((pct(cs) + '&' + pct(ats)).encode(), base_str.encode(), hashlib.sha1).digest()
).decode()
oauth['oauth_signature'] = sig
auth = 'OAuth ' + ', '.join(pct(k) + '="' + pct(v) + '"' for k, v in sorted(oauth.items()))

url = base_url + '?' + urllib.parse.urlencode(query_params)
req = urllib.request.Request(url)
req.add_header('Authorization', auth)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as r:
        print('STATUS:', r.status)
        print(r.read().decode()[:500])
except urllib.error.HTTPError as e:
    print('ERROR:', e.code, e.read().decode()[:500])
